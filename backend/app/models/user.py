import enum
from datetime import datetime
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class UserRole(enum.Enum):
    STUDENT = "student"
    DRIVER = "driver"
    ADMIN = "admin"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=True)
    phone = db.Column(db.String(20))

    password_hash = db.Column(db.String(200), nullable=False)

    role = db.Column(db.Enum(UserRole), default=UserRole.STUDENT, nullable=False)

    is_verified = db.Column(db.Boolean, default=False)
    account_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # --- Security hardening (Phase 1) ---
    # Withdrawal protection: any withdrawal is blocked while now() < withdrawal_locked_until.
    withdrawal_locked_until = db.Column(db.DateTime, nullable=True)

    # Global session revocation: any JWT with iat < tokens_invalidated_at is rejected.
    tokens_invalidated_at = db.Column(db.DateTime, nullable=True)

    # Brute-force / account lockout protection.
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)

    # Velocity-limit bookkeeping (reset windows are computed on read, not stored).
    password_changed_at = db.Column(db.DateTime, nullable=True)

    # relationships
    driver_profile = db.relationship(
        "Driver",
        back_populates="user",
        uselist=False,
        foreign_keys="Driver.user_id"
    )

    ride_requests = db.relationship(
        "RideRequest",
        back_populates="student",
        foreign_keys="RideRequest.student_id"
    )

    # ✅ FIXED: added missing relationship
    approved_drivers = db.relationship(
        "Driver",
        back_populates="approver",
        foreign_keys="Driver.approved_by"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "student_id": self.student_id,
            "phone": self.phone,
            "role": self.role.value,
            "is_verified": self.is_verified,
            "account_active": self.account_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def is_locked(self):
        return bool(self.locked_until and datetime.utcnow() < self.locked_until)

    def is_withdrawal_locked(self):
        return bool(self.withdrawal_locked_until and datetime.utcnow() < self.withdrawal_locked_until)

    def to_admin_dict(self):
        data = self.to_dict()
        data.update({
            "failed_login_attempts": self.failed_login_attempts,
            "locked_until": self.locked_until.isoformat() if self.locked_until else None,
            "is_locked": self.is_locked(),
            "withdrawal_locked_until": self.withdrawal_locked_until.isoformat() if self.withdrawal_locked_until else None,
            "is_withdrawal_locked": self.is_withdrawal_locked(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
        })
        return data