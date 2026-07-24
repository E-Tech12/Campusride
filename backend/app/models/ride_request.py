import enum
from datetime import datetime
from app.extensions import db


class RideRequestStatus(enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    PENDING = "pending"        # student requested, awaiting driver response
    ACCEPTED = "accepted"      # driver accepted, seat reserved
    REJECTED = "rejected"      # driver declined
    ONGOING = "ongoing"        # picked up, en route
    AWAITING_COMPLETION = "awaiting_completion"  # driver reached destination geofence, awaiting student confirmation
    COMPLETED = "completed"    # dropped off, funds released
    DISPUTED = "disputed"      # student reported a problem before confirming
    CANCELLED = "cancelled"    # student or driver cancelled before pickup


class RideRequest(db.Model):
    """A single student's seat booking on a driver's active route, to a specific stop/zone."""
    __tablename__ = "ride_requests"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey("routes.id"), nullable=False)
    zone_id = db.Column(db.Integer, db.ForeignKey("zones.id"), nullable=False)  # student's drop-off

    pickup_lat = db.Column(db.Float, nullable=True)
    pickup_lng = db.Column(db.Float, nullable=True)

    price = db.Column(db.Float, nullable=False)  # snapshot of zone price at request time
    payment_reference = db.Column(db.String(100), nullable=True) # links to wallet hold
    status = db.Column(db.Enum(RideRequestStatus), default=RideRequestStatus.PENDING, nullable=False)

    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime, nullable=True)
    picked_up_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    # --- Phase 2/3: real-time GPS + destination validation ---
    driver_near_pickup = db.Column(db.Boolean, default=False)   # entered outer pickup geofence
    driver_arrived_at = db.Column(db.DateTime, nullable=True)   # entered inner pickup geofence

    awaiting_completion_at = db.Column(db.DateTime, nullable=True)  # entered destination geofence
    completion_deadline = db.Column(db.DateTime, nullable=True)     # auto-release-if-no-response timeout

    dispute_reason = db.Column(db.String(500), nullable=True)
    disputed_at = db.Column(db.DateTime, nullable=True)

    student = db.relationship("User", back_populates="ride_requests", foreign_keys=[student_id])
    driver = db.relationship("Driver", back_populates="ride_requests", foreign_keys=[driver_id])
    route = db.relationship("Route")
    zone = db.relationship("Zone")

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student.full_name if self.student else None,
            "driver_id": self.driver_id,
            "route_id": self.route_id,
            "zone": self.zone.to_dict() if self.zone else None,
            "pickup_lat": self.pickup_lat,
            "pickup_lng": self.pickup_lng,
            "price": self.price,
            "status": self.status.value,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "picked_up_at": self.picked_up_at.isoformat() if self.picked_up_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "driver_near_pickup": self.driver_near_pickup,
            "driver_arrived_at": self.driver_arrived_at.isoformat() if self.driver_arrived_at else None,
            "awaiting_completion_at": self.awaiting_completion_at.isoformat() if self.awaiting_completion_at else None,
            "completion_deadline": self.completion_deadline.isoformat() if self.completion_deadline else None,
            "dispute_reason": self.dispute_reason,
            "disputed_at": self.disputed_at.isoformat() if self.disputed_at else None,
        }
