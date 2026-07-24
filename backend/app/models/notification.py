import enum
from datetime import datetime
from app.extensions import db


class NotificationEvent(enum.Enum):
    RIDE_ACCEPTED = "ride_accepted"
    DRIVER_APPROACHING = "driver_approaching"
    DRIVER_ARRIVED = "driver_arrived"
    RIDE_STARTED = "ride_started"
    RIDE_COMPLETED = "ride_completed"
    RIDE_AWAITING_CONFIRMATION = "ride_awaiting_confirmation"
    DISPUTE_OPENED = "dispute_opened"
    DEPOSIT_SUCCESSFUL = "deposit_successful"
    WITHDRAWAL_APPROVED = "withdrawal_approved"
    WITHDRAWAL_FAILED = "withdrawal_failed"
    PASSWORD_CHANGED = "password_changed"
    SUSPICIOUS_LOGIN = "suspicious_login"
    KYC_APPROVED = "kyc_approved"
    KYC_REJECTED = "kyc_rejected"


class DeviceToken(db.Model):
    """FCM registration token for a user's device. A user can have several
    (phone + browser, or multiple browsers), so this is not unique per user."""
    __tablename__ = "device_tokens"
    __table_args__ = (
        db.Index("idx_devicetoken_user", "user_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False)
    platform = db.Column(db.String(20), default="web")  # web, android, ios
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref="device_tokens")

    def to_dict(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class NotificationLog(db.Model):
    """History of every push notification the platform attempted to send,
    independent of whether FCM delivery actually succeeded."""
    __tablename__ = "notification_logs"
    __table_args__ = (
        db.Index("idx_notiflog_user_created", "user_id", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event = db.Column(db.Enum(NotificationEvent), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    body = db.Column(db.String(500), nullable=False)
    data = db.Column(db.JSON)
    delivered = db.Column(db.Boolean, default=False)
    error = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="notifications")

    def to_dict(self):
        return {
            "id": self.id,
            "event": self.event.value if self.event else None,
            "title": self.title,
            "body": self.body,
            "data": self.data,
            "delivered": self.delivered,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
