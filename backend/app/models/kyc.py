import enum
from datetime import datetime
from app.extensions import db


class KYCStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DriverKYC(db.Model):
    """Identity verification record for a driver. A driver can resubmit after
    rejection, so this keeps history rather than being a single row that gets
    overwritten -- only the latest row for a driver_id is authoritative."""
    __tablename__ = "driver_kyc"
    __table_args__ = (
        db.Index("idx_kyc_driver_created", "driver_id", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"), nullable=False, index=True)

    government_id_url = db.Column(db.String(500), nullable=False)
    government_id_type = db.Column(db.String(50))  # e.g. national_id, passport, voters_card
    selfie_url = db.Column(db.String(500), nullable=False)
    drivers_license_url = db.Column(db.String(500), nullable=False)
    proof_of_ownership_url = db.Column(db.String(500), nullable=True)

    status = db.Column(db.Enum(KYCStatus), default=KYCStatus.PENDING, nullable=False)
    rejection_reason = db.Column(db.String(500), nullable=True)

    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    driver = db.relationship("Driver", backref="kyc_submissions")
    reviewer = db.relationship("User", foreign_keys=[reviewed_by])

    def to_dict(self, include_documents=True):
        data = {
            "id": self.id,
            "driver_id": self.driver_id,
            "driver_name": self.driver.user.full_name if self.driver and self.driver.user else None,
            "government_id_type": self.government_id_type,
            "status": self.status.value if self.status else None,
            "rejection_reason": self.rejection_reason,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_documents:
            data.update({
                "government_id_url": self.government_id_url,
                "selfie_url": self.selfie_url,
                "drivers_license_url": self.drivers_license_url,
                "proof_of_ownership_url": self.proof_of_ownership_url,
            })
        return data
