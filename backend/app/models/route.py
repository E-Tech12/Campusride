from datetime import datetime
from app.extensions import db


class Zone(db.Model):
    """A pricing zone, e.g. 'Main Gate', 'Hostel Block C'. Price is per-zone, not per-distance."""
    __tablename__ = "zones"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)  # price to be dropped off in/at this zone
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "lat": self.lat,
            "lng": self.lng,
            "is_active": self.is_active,
        }


class Route(db.Model):
    __tablename__ = "routes"

    id = db.Column(db.Integer, primary_key=True)

    driver_id = db.Column(
        db.Integer,
        db.ForeignKey("drivers.id"),
        nullable=False
    )

    name = db.Column(
        db.String(120),
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    driver = db.relationship(
        "Driver",
        back_populates="routes",
        foreign_keys=[driver_id]
    )

    stops = db.relationship(
        "RouteStop",
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="RouteStop.sequence"
    )

    def to_dict(self, include_stops=True):
        data = {
            "id": self.id,
            "driver_id": self.driver_id,
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_stops:
            data["stops"] = [s.to_dict() for s in self.stops]
        return data

class RouteStop(db.Model):
    """A single stop on a route, in order, linked to a pricing zone."""
    __tablename__ = "route_stops"

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey("routes.id"), nullable=False)
    zone_id = db.Column(db.Integer, db.ForeignKey("zones.id"), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)  # order along the route, 0-indexed

    route = db.relationship("Route", back_populates="stops")
    zone = db.relationship("Zone")

    def to_dict(self):
        return {
            "id": self.id,
            "route_id": self.route_id,
            "sequence": self.sequence,
            "zone": self.zone.to_dict() if self.zone else None,
        }