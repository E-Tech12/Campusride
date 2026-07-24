import os
import hashlib
from datetime import datetime, timedelta

from app.extensions import db
from app.models import (
    User, SecurityLog, SecurityEventType,
    LoginSecurity, OTP,
    WithdrawalRequest, WithdrawalStatus,
)

try:
    from user_agents import parse as parse_user_agent
except ImportError:  # pragma: no cover - package should always be installed per requirements.txt
    parse_user_agent = None


# ---------------------------------------------------------------------------
# Configurable limits (all overridable via environment variables so ops can
# tune them without a deploy).
# ---------------------------------------------------------------------------
def _env_float(name, default):
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return float(default)


def _env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return int(default)


WITHDRAWAL_LOCK_HOURS = _env_float("WITHDRAWAL_LOCK_HOURS", 24)
WITHDRAWAL_SINGLE_MAX = _env_float("WITHDRAWAL_SINGLE_MAX", 50000)
WITHDRAWAL_DAILY_MAX = _env_float("WITHDRAWAL_DAILY_MAX", 100000)
WITHDRAWAL_WEEKLY_MAX = _env_float("WITHDRAWAL_WEEKLY_MAX", 300000)

WITHDRAWAL_MAX_PER_DAY = _env_int("WITHDRAWAL_MAX_PER_DAY", 3)
OTP_MAX_PER_HOUR = _env_int("OTP_MAX_PER_HOUR", 10)
PASSWORD_RESET_MAX_PER_DAY = _env_int("PASSWORD_RESET_MAX_PER_DAY", 5)

ACCOUNT_LOCKOUT_THRESHOLD = _env_int("ACCOUNT_LOCKOUT_THRESHOLD", 5)
ACCOUNT_LOCKOUT_MINUTES = _env_float("ACCOUNT_LOCKOUT_MINUTES", 15)

COMPLETION_AUTO_RELEASE_MINUTES = _env_float("COMPLETION_AUTO_RELEASE_MINUTES", 30)
GEOFENCE_NEAR_PICKUP_METERS = _env_float("GEOFENCE_NEAR_PICKUP_METERS", 150)
GEOFENCE_ARRIVED_METERS = _env_float("GEOFENCE_ARRIVED_METERS", 50)
GEOFENCE_DESTINATION_METERS = _env_float("GEOFENCE_DESTINATION_METERS", 100)


# ---------------------------------------------------------------------------
# Request metadata helpers
# ---------------------------------------------------------------------------
def get_request_ip(request):
    """Respect a trusted reverse proxy's X-Forwarded-For if present, else the
    direct peer address."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def parse_device(user_agent_string):
    """Returns (browser, os, device_type, device_hash). Falls back gracefully
    if the user-agents package isn't available or the string is empty."""
    if not user_agent_string or not parse_user_agent:
        return "unknown", "unknown", "unknown", hashlib.sha256(b"unknown").hexdigest()[:32]

    ua = parse_user_agent(user_agent_string)
    browser = f"{ua.browser.family} {ua.browser.version_string}".strip()
    os_name = f"{ua.os.family} {ua.os.version_string}".strip()
    if ua.is_mobile:
        device_type = "mobile"
    elif ua.is_tablet:
        device_type = "tablet"
    elif ua.is_pc:
        device_type = "desktop"
    else:
        device_type = "other"

    fingerprint_source = f"{ua.browser.family}|{ua.os.family}|{device_type}"
    device_hash = hashlib.sha256(fingerprint_source.encode()).hexdigest()[:32]
    return browser, os_name, device_type, device_hash


# ---------------------------------------------------------------------------
# Account lockout (brute-force protection)
# ---------------------------------------------------------------------------
def register_failed_login(user, ip_address=None, user_agent=None):
    user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
    SecurityLog.record(
        user.id, SecurityEventType.LOGIN_FAILED,
        description=f"Failed login attempt #{user.failed_login_attempts}",
        ip_address=ip_address, user_agent=user_agent,
    )
    if user.failed_login_attempts >= ACCOUNT_LOCKOUT_THRESHOLD:
        user.locked_until = datetime.utcnow() + timedelta(minutes=ACCOUNT_LOCKOUT_MINUTES)
        SecurityLog.record(
            user.id, SecurityEventType.ACCOUNT_LOCKED,
            description=f"Account locked for {ACCOUNT_LOCKOUT_MINUTES} minutes after "
                        f"{user.failed_login_attempts} failed attempts",
            ip_address=ip_address, user_agent=user_agent,
        )
    db.session.commit()


def reset_failed_login(user):
    if user.failed_login_attempts or user.locked_until:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()


def check_account_lockout(user):
    """Returns an error message string if the account is currently locked,
    else None."""
    if user.is_locked():
        remaining = int((user.locked_until - datetime.utcnow()).total_seconds() / 60) + 1
        return f"Account temporarily locked due to repeated failed logins. Try again in {remaining} minute(s)."
    return None


# ---------------------------------------------------------------------------
# Device / login monitoring + risk scoring
# ---------------------------------------------------------------------------
def record_login(user, request, successful=True):
    """Creates a LoginSecurity row, detects new device / new location, and
    computes a simple risk score. Returns the LoginSecurity row so callers can
    decide whether to require step-up OTP verification.

    Note: country/city are left null here -- plug in a GeoIP provider (e.g.
    MaxMind, ipapi) by populating them before calling this function if one is
    configured for the deployment."""
    ip_address = get_request_ip(request)
    user_agent_string = request.headers.get("User-Agent", "")
    browser, os_name, device_type, device_hash = parse_device(user_agent_string)

    is_new_device = not LoginSecurity.query.filter_by(
        user_id=user.id, device_hash=device_hash, successful=True
    ).first()
    is_new_location = not LoginSecurity.query.filter_by(
        user_id=user.id, ip_address=ip_address, successful=True
    ).first()

    risk_score = 0
    if is_new_device:
        risk_score += 40
    if is_new_location:
        risk_score += 30
    if not successful:
        risk_score += 20

    entry = LoginSecurity(
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent_string[:255],
        browser=browser[:80],
        operating_system=os_name[:80],
        device_type=device_type,
        device_hash=device_hash,
        successful=successful,
        is_new_device=is_new_device,
        is_new_location=is_new_location,
        risk_score=min(risk_score, 100),
    )
    db.session.add(entry)

    if successful and (is_new_device or is_new_location):
        SecurityLog.record(
            user.id,
            SecurityEventType.LOGIN_NEW_DEVICE if is_new_device else SecurityEventType.LOGIN_NEW_LOCATION,
            description=f"Login from {'a new device' if is_new_device else 'a new location'} "
                        f"({browser} on {os_name}, {ip_address})",
            ip_address=ip_address, user_agent=user_agent_string[:255],
        )
    db.session.commit()

    if successful:
        from app.services import fraud_service
        fraud_service.check_suspicious_login(user.id, entry)
        fraud_service.check_rapid_device_change(user.id)

    return entry


def login_requires_step_up_otp(login_entry):
    """High-risk-action policy: a new device AND new location together (or a
    risk score >= 60) requires OTP verification before the session is fully
    trusted, even though the password was correct."""
    return login_entry.risk_score >= 60


# ---------------------------------------------------------------------------
# Global session revocation
# ---------------------------------------------------------------------------
def revoke_all_sessions(user, reason="Password changed"):
    """Any JWT already issued with iat earlier than this timestamp will be
    rejected by the token_in_blocklist_loader in app/__init__.py."""
    user.tokens_invalidated_at = datetime.utcnow()
    SecurityLog.record(user.id, SecurityEventType.SESSIONS_REVOKED, description=reason)
    db.session.commit()


def lock_withdrawals(user, reason):
    """Called after password/email/phone changes. Blocks withdrawals for
    WITHDRAWAL_LOCK_HOURS."""
    user.withdrawal_locked_until = datetime.utcnow() + timedelta(hours=WITHDRAWAL_LOCK_HOURS)
    SecurityLog.record(
        user.id, SecurityEventType.WITHDRAWAL_BLOCKED_LOCK,
        description=f"Withdrawal lock applied for {WITHDRAWAL_LOCK_HOURS}h following: {reason}",
    )
    db.session.commit()


# ---------------------------------------------------------------------------
# Withdrawal limits + velocity
# ---------------------------------------------------------------------------
def check_withdrawal_allowed(user, driver_id, amount):
    """Runs every pre-withdrawal check. Returns an error message string on
    rejection (and logs a SecurityLog entry), or None if the withdrawal may
    proceed."""
    now = datetime.utcnow()

    if user.is_withdrawal_locked():
        remaining_hours = round((user.withdrawal_locked_until - now).total_seconds() / 3600, 1)
        SecurityLog.record(
            user.id, SecurityEventType.WITHDRAWAL_BLOCKED_LOCK,
            description=f"Withdrawal attempt blocked, {remaining_hours}h remaining on lock",
        )
        db.session.commit()
        return "Withdrawals temporarily locked due to recent account security change."

    if amount > WITHDRAWAL_SINGLE_MAX:
        SecurityLog.record(
            user.id, SecurityEventType.WITHDRAWAL_BLOCKED_LIMIT,
            description=f"Single withdrawal {amount} exceeds max {WITHDRAWAL_SINGLE_MAX}",
        )
        db.session.commit()
        return f"Single withdrawal cannot exceed {WITHDRAWAL_SINGLE_MAX:,.2f}."

    today_start = datetime.combine(now.date(), datetime.min.time())
    week_start = now - timedelta(days=7)

    todays_withdrawals = db.session.query(WithdrawalRequest).filter(
        WithdrawalRequest.driver_id == driver_id,
        WithdrawalRequest.created_at >= today_start,
        WithdrawalRequest.status.in_([WithdrawalStatus.PENDING, WithdrawalStatus.APPROVED]),
    ).all()
    weeks_withdrawals = db.session.query(WithdrawalRequest).filter(
        WithdrawalRequest.driver_id == driver_id,
        WithdrawalRequest.created_at >= week_start,
        WithdrawalRequest.status.in_([WithdrawalStatus.PENDING, WithdrawalStatus.APPROVED]),
    ).all()

    today_total = sum(w.amount for w in todays_withdrawals)
    week_total = sum(w.amount for w in weeks_withdrawals)

    if today_total + amount > WITHDRAWAL_DAILY_MAX:
        SecurityLog.record(
            user.id, SecurityEventType.WITHDRAWAL_BLOCKED_LIMIT,
            description=f"Daily withdrawal total would reach {today_total + amount}, "
                        f"exceeding max {WITHDRAWAL_DAILY_MAX}",
        )
        db.session.commit()
        return f"This would exceed your daily withdrawal limit of {WITHDRAWAL_DAILY_MAX:,.2f}."

    if week_total + amount > WITHDRAWAL_WEEKLY_MAX:
        SecurityLog.record(
            user.id, SecurityEventType.WITHDRAWAL_BLOCKED_LIMIT,
            description=f"Weekly withdrawal total would reach {week_total + amount}, "
                        f"exceeding max {WITHDRAWAL_WEEKLY_MAX}",
        )
        db.session.commit()
        return f"This would exceed your weekly withdrawal limit of {WITHDRAWAL_WEEKLY_MAX:,.2f}."

    if len(todays_withdrawals) >= WITHDRAWAL_MAX_PER_DAY:
        SecurityLog.record(
            user.id, SecurityEventType.WITHDRAWAL_BLOCKED_VELOCITY,
            description=f"Already made {len(todays_withdrawals)} withdrawals today "
                        f"(max {WITHDRAWAL_MAX_PER_DAY})",
        )
        db.session.commit()
        return f"You've reached the maximum of {WITHDRAWAL_MAX_PER_DAY} withdrawals per day."

    return None


# ---------------------------------------------------------------------------
# OTP velocity limits
# ---------------------------------------------------------------------------
def request_high_risk_otp(user, purpose):
    """Issues an OTP (reusing the existing OTP model/table) for a sensitive
    action: withdrawal, email change, password change, bank account change.
    Returns an error message on rate-limit rejection, else None (and the
    email has been sent)."""
    from datetime import timedelta as _td
    from app.utils.email import send_otp_email

    velocity_error = check_otp_velocity(user, purpose)
    if velocity_error:
        return velocity_error

    otp_code = OTP.generate_otp()
    otp = OTP(
        user_id=user.id,
        email=user.email,
        otp_code=otp_code,
        purpose=purpose,
        expires_at=datetime.utcnow() + _td(minutes=10),
    )
    db.session.add(otp)
    SecurityLog.record(user.id, SecurityEventType.OTP_REQUESTED, description=f"OTP requested for {purpose}")
    db.session.commit()
    try:
        send_otp_email(email=user.email, otp_code=otp_code, purpose=purpose)
    except Exception:
        pass  # Delivery failure shouldn't block the flow; user can request a resend.
    return None


def verify_high_risk_otp(user, purpose, otp_code):
    """Returns an error message on failure, else None and marks the OTP used."""
    if not otp_code:
        return "Verification code required for this action."

    otp = (
        OTP.query.filter_by(user_id=user.id, purpose=purpose, otp_code=otp_code)
        .order_by(OTP.created_at.desc())
        .first()
    )
    if not otp or not otp.is_valid():
        SecurityLog.record(user.id, SecurityEventType.OTP_FAILED, description=f"Invalid/expired OTP for {purpose}")
        db.session.commit()
        from app.services import fraud_service
        fraud_service.check_repeated_otp_failures(user.id)
        return "Invalid or expired verification code."

    otp.use()
    SecurityLog.record(user.id, SecurityEventType.HIGH_RISK_ACTION_VERIFIED, description=f"OTP verified for {purpose}")
    db.session.commit()
    return None


def check_otp_velocity(user, purpose):
    """Enforces max OTP requests/hour and max password-reset requests/day."""
    now = datetime.utcnow()
    hour_ago = now - timedelta(hours=1)
    day_ago = now - timedelta(days=1)

    otp_last_hour = OTP.query.filter(
        OTP.user_id == user.id, OTP.created_at >= hour_ago
    ).count()
    if otp_last_hour >= OTP_MAX_PER_HOUR:
        SecurityLog.record(
            user.id, SecurityEventType.OTP_RATE_LIMITED,
            description=f"{otp_last_hour} OTP requests in the last hour (max {OTP_MAX_PER_HOUR})",
        )
        db.session.commit()
        return "Too many verification code requests. Please try again later."

    if purpose == "password_reset":
        resets_today = OTP.query.filter(
            OTP.user_id == user.id, OTP.purpose == "password_reset", OTP.created_at >= day_ago
        ).count()
        if resets_today >= PASSWORD_RESET_MAX_PER_DAY:
            SecurityLog.record(
                user.id, SecurityEventType.OTP_RATE_LIMITED,
                description=f"{resets_today} password reset requests today (max {PASSWORD_RESET_MAX_PER_DAY})",
            )
            db.session.commit()
            return "Too many password reset requests today. Please try again tomorrow."

    return None
