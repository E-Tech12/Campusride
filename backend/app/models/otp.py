import secrets
from datetime import datetime, timedelta
from app.extensions import db


class OTP(db.Model):
    __tablename__ = "otps"
    __table_args__ = (
        db.Index("idx_otp_user_purpose", "user_id", "purpose"),
        db.Index("idx_otp_expires_at", "expires_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(20), nullable=False)  # email_verification, password_reset, login
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="otps")

    def is_valid(self):
        return not self.is_used and datetime.utcnow() < self.expires_at

    def use(self):
        self.is_used = True
        db.session.commit()

    @staticmethod
    def generate_otp():
        return str(secrets.randbelow(1000000)).zfill(6)

    @staticmethod
    def cleanup_expired():
        threshold = datetime.utcnow() - timedelta(hours=1)
        deleted = OTP.query.filter(OTP.created_at < threshold).delete()
        db.session.commit()
        return deleted


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"
    __table_args__ = (
        db.Index("idx_token_value", "token"),
        db.Index("idx_token_expires", "expires_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="reset_tokens")

    def is_valid(self):
        return not self.is_used and datetime.utcnow() < self.expires_at

    def use(self):
        self.is_used = True
        db.session.commit()

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)

    @staticmethod
    def cleanup_expired():
        threshold = datetime.utcnow() - timedelta(days=1)
        deleted = PasswordResetToken.query.filter(
            PasswordResetToken.created_at < threshold
        ).delete()
        db.session.commit()
        return deleted
