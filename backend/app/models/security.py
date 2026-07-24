import enum
from datetime import datetime
from app.extensions import db


class SecurityEventType(enum.Enum):
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"
    EMAIL_CHANGED = "email_changed"
    PHONE_CHANGED = "phone_changed"
    BANK_ACCOUNT_CHANGED = "bank_account_changed"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGIN_NEW_DEVICE = "login_new_device"
    LOGIN_NEW_LOCATION = "login_new_location"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    SESSIONS_REVOKED = "sessions_revoked"
    WITHDRAWAL_BLOCKED_LOCK = "withdrawal_blocked_lock"
    WITHDRAWAL_BLOCKED_LIMIT = "withdrawal_blocked_limit"
    WITHDRAWAL_BLOCKED_VELOCITY = "withdrawal_blocked_velocity"
    WITHDRAWAL_REQUESTED = "withdrawal_requested"
    OTP_REQUESTED = "otp_requested"
    OTP_FAILED = "otp_failed"
    OTP_RATE_LIMITED = "otp_rate_limited"
    HIGH_RISK_ACTION_VERIFIED = "high_risk_action_verified"
    KYC_SUBMITTED = "kyc_submitted"
    KYC_APPROVED = "kyc_approved"
    KYC_REJECTED = "kyc_rejected"
    FRAUD_ALERT_RAISED = "fraud_alert_raised"


class SecurityLog(db.Model):
    """Append-only audit trail of every security-relevant event on the
    platform. Used to drive the admin security dashboard and to reconstruct
    what happened around a disputed withdrawal or account compromise."""
    __tablename__ = "security_logs"
    __table_args__ = (
        db.Index("idx_seclog_user_created", "user_id", "created_at"),
        db.Index("idx_seclog_event_created", "event_type", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    event_type = db.Column(db.Enum(SecurityEventType), nullable=False)
    description = db.Column(db.String(255))
    ip_address = db.Column(db.String(64))
    user_agent = db.Column(db.String(255))
    meta_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship("User", backref="security_logs")

    @staticmethod
    def record(user_id, event_type, description=None, ip_address=None, user_agent=None, meta_data=None):
        log = SecurityLog(
            user_id=user_id,
            event_type=event_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            meta_data=meta_data,
        )
        db.session.add(log)
        return log

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else None,
            "event_type": self.event_type.value if self.event_type else None,
            "description": self.description,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "meta_data": self.meta_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class LoginSecurity(db.Model):
    """One row per login attempt (successful or not). Powers new-device /
    new-location detection and the admin device-history view."""
    __tablename__ = "login_security"
    __table_args__ = (
        db.Index("idx_loginsec_user_created", "user_id", "created_at"),
        db.Index("idx_loginsec_device_hash", "user_id", "device_hash"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    ip_address = db.Column(db.String(64))
    user_agent = db.Column(db.String(255))
    browser = db.Column(db.String(80))
    operating_system = db.Column(db.String(80))
    device_type = db.Column(db.String(40))
    device_hash = db.Column(db.String(64), index=True)  # fingerprint of (browser+os+device_type)

    country = db.Column(db.String(80), nullable=True)
    city = db.Column(db.String(80), nullable=True)

    successful = db.Column(db.Boolean, default=True, nullable=False)
    is_new_device = db.Column(db.Boolean, default=False)
    is_new_location = db.Column(db.Boolean, default=False)
    risk_score = db.Column(db.Integer, default=0)  # 0-100

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship("User", backref="login_history")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "browser": self.browser,
            "operating_system": self.operating_system,
            "device_type": self.device_type,
            "country": self.country,
            "city": self.city,
            "successful": self.successful,
            "is_new_device": self.is_new_device,
            "is_new_location": self.is_new_location,
            "risk_score": self.risk_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class FraudAlertSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FraudAlertStatus(enum.Enum):
    OPEN = "open"
    REVIEWING = "reviewing"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class FraudAlertType(enum.Enum):
    UNUSUAL_WITHDRAWAL = "unusual_withdrawal"
    REPEATED_OTP_FAILURES = "repeated_otp_failures"
    RAPID_DEVICE_CHANGE = "rapid_device_change"
    SUSPICIOUS_LOGIN_LOCATION = "suspicious_login_location"
    EXCESSIVE_RIDE_CREATION = "excessive_ride_creation"
    EXCESSIVE_CANCELLATION = "excessive_cancellation"
    ABNORMAL_TRANSACTION_PATTERN = "abnormal_transaction_pattern"


class FraudAlert(db.Model):
    __tablename__ = "fraud_alerts"
    __table_args__ = (
        db.Index("idx_fraud_user_status", "user_id", "status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    alert_type = db.Column(db.Enum(FraudAlertType), nullable=False)
    severity = db.Column(db.Enum(FraudAlertSeverity), default=FraudAlertSeverity.MEDIUM, nullable=False)
    reason = db.Column(db.String(500), nullable=False)
    status = db.Column(db.Enum(FraudAlertStatus), default=FraudAlertStatus.OPEN, nullable=False)
    meta_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    resolution_notes = db.Column(db.String(500))

    user = db.relationship("User", foreign_keys=[user_id], backref="fraud_alerts")
    resolver = db.relationship("User", foreign_keys=[resolved_by])

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else None,
            "alert_type": self.alert_type.value if self.alert_type else None,
            "severity": self.severity.value if self.severity else None,
            "reason": self.reason,
            "status": self.status.value if self.status else None,
            "meta_data": self.meta_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "resolution_notes": self.resolution_notes,
        }
