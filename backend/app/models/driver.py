import enum
from datetime import datetime
from app.extensions import db


class DriverStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class Driver(db.Model):
    __tablename__ = "drivers"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    vehicle_make = db.Column(db.String(50), nullable=False)
    vehicle_model = db.Column(db.String(50), nullable=False)
    vehicle_color = db.Column(db.String(30), nullable=False)

    plate_number = db.Column(db.String(20), unique=True, nullable=False)

    seat_capacity = db.Column(db.Integer, nullable=False, default=4)

    license_number = db.Column(db.String(50), nullable=False)

    status = db.Column(
        db.Enum(DriverStatus),
        default=DriverStatus.PENDING,
        nullable=False
    )

    approved_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.String(255))

    is_online = db.Column(db.Boolean, default=False)

    current_lat = db.Column(db.Float)
    current_lng = db.Column(db.Float)

    last_location_update = db.Column(db.DateTime)

    # The route a driver is currently running while online. Nullable because a
    # driver may have zero or many saved routes but only one (or none) active.
    active_route_id = db.Column(
        db.Integer,
        db.ForeignKey("routes.id", use_alter=True, name="fk_driver_active_route"),
        nullable=True
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    user = db.relationship(
        "User",
        back_populates="driver_profile",
        foreign_keys=[user_id]
    )

    approver = db.relationship(
        "User",
        back_populates="approved_drivers",
        foreign_keys=[approved_by]
    )

    routes = db.relationship(
        "Route",
        back_populates="driver",
        cascade="all, delete-orphan",
        foreign_keys="Route.driver_id"
    )

    active_route = db.relationship(
        "Route",
        foreign_keys=[active_route_id],
        post_update=True
    )

    ride_requests = db.relationship(
        "RideRequest",
        back_populates="driver"
    )

    def seats_available(self):
        """Seats left on the driver's current run: capacity minus every rider
        currently occupying a seat (accepted but not yet picked up, or ongoing)."""
        from app.models.ride_request import RideRequest, RideRequestStatus
        taken = RideRequest.query.filter(
            RideRequest.driver_id == self.id,
            RideRequest.status.in_([RideRequestStatus.ACCEPTED, RideRequestStatus.ONGOING])
        ).count()
        return max(self.seat_capacity - taken, 0)

    def to_dict(self, include_contact=False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.user.full_name if self.user else None,
            "vehicle_make": self.vehicle_make,
            "vehicle_model": self.vehicle_model,
            "vehicle_color": self.vehicle_color,
            "plate_number": self.plate_number,
            "seat_capacity": self.seat_capacity,
            "seats_available": self.seats_available(),
            "license_number": self.license_number,
            "status": self.status.value if self.status else None,
            "is_online": self.is_online,
            "current_lat": self.current_lat,
            "current_lng": self.current_lng,
            "last_location_update": self.last_location_update.isoformat() if self.last_location_update else None,
            "active_route_id": self.active_route_id,
            "active_route": self.active_route.to_dict() if self.active_route else None,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_contact and self.user:
            data["email"] = self.user.email
            data["phone"] = self.user.phone
        return data