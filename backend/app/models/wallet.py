import enum
from datetime import datetime
from app.extensions import db

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    RIDE_PAYMENT = "ride_payment"
    RIDE_REFUND = "ride_refund"
    DRIVER_EARNING = "driver_earning"
    PLATFORM_COMMISSION = "platform_commission"

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class Wallet(db.Model):
    __tablename__ = "wallets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0, nullable=False)
    pending_balance = db.Column(db.Float, default=0.0, nullable=False) # For holding funds during a ride
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("wallet", uselist=False))

class WalletTransaction(db.Model):
    __tablename__ = "wallet_transactions"
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    status = db.Column(db.Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    reference = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    wallet = db.relationship("Wallet", backref="transactions")

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "type": self.transaction_type.value,
            "status": self.status.value,
            "reference": self.reference,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

class WithdrawalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"

class WithdrawalRequest(db.Model):
    __tablename__ = "withdrawal_requests"
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(WithdrawalStatus), default=WithdrawalStatus.PENDING, nullable=False)
    bank_code = db.Column(db.String(50))
    account_number = db.Column(db.String(50))
    account_name = db.Column(db.String(100))
    reference = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)

    driver = db.relationship("Driver", backref="withdrawal_requests")

    def to_dict(self):
        return {
            "id": self.id,
            "driver_id": self.driver_id,
            "driver_name": self.driver.user.full_name if self.driver and self.driver.user else None,
            "amount": self.amount,
            "status": self.status.value,
            "bank_code": self.bank_code,
            "account_number": self.account_number,
            "account_name": self.account_name,
            "reference": self.reference,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }
