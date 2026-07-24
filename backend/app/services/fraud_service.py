import os
from datetime import datetime, timedelta

from app.extensions import db
from app.models import (
    FraudAlert, FraudAlertType, FraudAlertSeverity,
    SecurityLog, SecurityEventType,
    LoginSecurity, WithdrawalRequest, WithdrawalStatus,
    RideRequest, RideRequestStatus,
)


def _env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return int(default)


def _env_float(name, default):
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return float(default)


UNUSUAL_WITHDRAWAL_MULTIPLIER = _env_float("FRAUD_UNUSUAL_WITHDRAWAL_MULTIPLIER", 3.0)
OTP_FAILURE_THRESHOLD = _env_int("FRAUD_OTP_FAILURE_THRESHOLD", 4)
DEVICE_CHANGE_THRESHOLD = _env_int("FRAUD_DEVICE_CHANGE_THRESHOLD", 3)
EXCESSIVE_RIDES_THRESHOLD = _env_int("FRAUD_EXCESSIVE_RIDES_PER_HOUR", 8)
EXCESSIVE_CANCELLATION_THRESHOLD = _env_int("FRAUD_EXCESSIVE_CANCELLATIONS_PER_DAY", 5)


def _raise_alert(user_id, alert_type, severity, reason, meta_data=None):
    alert = FraudAlert(
        user_id=user_id, alert_type=alert_type, severity=severity,
        reason=reason, meta_data=meta_data or {},
    )
    db.session.add(alert)
    SecurityLog.record(user_id, SecurityEventType.FRAUD_ALERT_RAISED, description=reason)
    db.session.commit()
    return alert


def check_unusual_withdrawal(user_id, driver_id, amount):
    """Flags a withdrawal that's far larger than the driver's historical
    average -- a common signal of a compromised account cashing out fast."""
    past = WithdrawalRequest.query.filter(
        WithdrawalRequest.driver_id == driver_id,
        WithdrawalRequest.status == WithdrawalStatus.APPROVED,
    ).all()
    if len(past) < 3:
        return None  # not enough history to establish a baseline

    avg = sum(w.amount for w in past) / len(past)
    if avg > 0 and amount > avg * UNUSUAL_WITHDRAWAL_MULTIPLIER:
        return _raise_alert(
            user_id, FraudAlertType.UNUSUAL_WITHDRAWAL, FraudAlertSeverity.HIGH,
            reason=f"Withdrawal of {amount:,.2f} is {amount / avg:.1f}x the driver's average "
                   f"of {avg:,.2f} over {len(past)} past payouts",
            meta_data={"amount": amount, "average": avg, "sample_size": len(past)},
        )
    return None


def check_repeated_otp_failures(user_id):
    since = datetime.utcnow() - timedelta(hours=1)
    failures = SecurityLog.query.filter(
        SecurityLog.user_id == user_id,
        SecurityLog.event_type == SecurityEventType.OTP_FAILED,
        SecurityLog.created_at >= since,
    ).count()
    if failures >= OTP_FAILURE_THRESHOLD:
        return _raise_alert(
            user_id, FraudAlertType.REPEATED_OTP_FAILURES, FraudAlertSeverity.MEDIUM,
            reason=f"{failures} failed OTP verifications in the last hour",
            meta_data={"failures": failures},
        )
    return None


def check_rapid_device_change(user_id):
    since = datetime.utcnow() - timedelta(hours=24)
    recent_devices = db.session.query(LoginSecurity.device_hash).filter(
        LoginSecurity.user_id == user_id,
        LoginSecurity.created_at >= since,
        LoginSecurity.successful == True,  # noqa: E712
    ).distinct().count()
    if recent_devices >= DEVICE_CHANGE_THRESHOLD:
        return _raise_alert(
            user_id, FraudAlertType.RAPID_DEVICE_CHANGE, FraudAlertSeverity.MEDIUM,
            reason=f"{recent_devices} distinct devices used to log in within 24 hours",
            meta_data={"distinct_devices": recent_devices},
        )
    return None


def check_suspicious_login(user_id, login_entry):
    if login_entry.risk_score >= 80:
        return _raise_alert(
            user_id, FraudAlertType.SUSPICIOUS_LOGIN_LOCATION, FraudAlertSeverity.HIGH,
            reason=f"Login from new device AND new location, risk score {login_entry.risk_score}",
            meta_data={"ip": login_entry.ip_address, "risk_score": login_entry.risk_score},
        )
    return None


def check_excessive_ride_creation(user_id):
    since = datetime.utcnow() - timedelta(hours=1)
    count = RideRequest.query.filter(
        RideRequest.student_id == user_id, RideRequest.requested_at >= since
    ).count()
    if count >= EXCESSIVE_RIDES_THRESHOLD:
        return _raise_alert(
            user_id, FraudAlertType.EXCESSIVE_RIDE_CREATION, FraudAlertSeverity.MEDIUM,
            reason=f"{count} ride requests created in the last hour",
            meta_data={"count": count},
        )
    return None


def check_excessive_cancellation(user_id):
    since = datetime.utcnow() - timedelta(days=1)
    count = RideRequest.query.filter(
        RideRequest.student_id == user_id,
        RideRequest.status == RideRequestStatus.CANCELLED,
        RideRequest.requested_at >= since,
    ).count()
    if count >= EXCESSIVE_CANCELLATION_THRESHOLD:
        return _raise_alert(
            user_id, FraudAlertType.EXCESSIVE_CANCELLATION, FraudAlertSeverity.LOW,
            reason=f"{count} ride cancellations in the last 24 hours",
            meta_data={"count": count},
        )
    return None
