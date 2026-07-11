from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db, socketio
from app.models import User, Driver, DriverStatus, Route, RouteStop, Zone, RideRequest, RideRequestStatus
from app.utils.decorators import student_required
from app.utils.geo import haversine_km, eta_minutes

ride_bp = Blueprint("ride", __name__, url_prefix="/api/rides")


def enrich_ride_request(ride_req, driver=None):
    """Attach live distance/ETA from the driver's current position to the
    student's pickup point. Computed on read (not persisted) since the
    driver keeps moving."""
    data = ride_req.to_dict()
    driver = driver or ride_req.driver
    distance = None
    if driver and driver.current_lat is not None and ride_req.pickup_lat is not None:
        distance = haversine_km(driver.current_lat, driver.current_lng, ride_req.pickup_lat, ride_req.pickup_lng)
    data["distance_km"] = round(distance, 2) if distance is not None else None
    data["eta_minutes"] = eta_minutes(distance)
    return data


@ride_bp.route("/nearby-drivers", methods=["GET"])
@jwt_required()
def nearby_drivers():
    """Returns online, approved drivers with seats available, sorted by distance from the student."""
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius_km = request.args.get("radius_km", default=5, type=float)

    q = Driver.query.filter_by(status=DriverStatus.APPROVED, is_online=True)

    if lat is not None and lng is not None:
        import math
        delta_lat = radius_km / 111.0
        delta_lng = radius_km / (111.0 * max(0.01, math.cos(math.radians(lat)))) if -90 <= lat <= 90 else delta_lat
        
        q = q.filter(
            Driver.current_lat.between(lat - delta_lat, lat + delta_lat),
            Driver.current_lng.between(lng - delta_lng, lng + delta_lng)
        )

    drivers = q.all()

    results = []
    for d in drivers:
        if d.seats_available() <= 0:
            continue
        distance = None
        if lat is not None and lng is not None and d.current_lat is not None:
            distance = haversine_km(lat, lng, d.current_lat, d.current_lng)
            if distance is not None and distance > radius_km:
                continue
        data = d.to_dict()
        data["distance_km"] = round(distance, 2) if distance is not None else None
        data["eta_minutes"] = eta_minutes(distance)
        results.append(data)

    results.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"]))
    return jsonify(results), 200


@ride_bp.route("/drivers/<int:driver_id>", methods=["GET"])
@jwt_required()
def driver_detail(driver_id):
    """Detail view when a student taps a driver pin: route, stops with prices, seats left."""
    driver = Driver.query.get(driver_id)
    if not driver or driver.status != DriverStatus.APPROVED:
        return jsonify({"error": "Driver not found"}), 404
    return jsonify(driver.to_dict()), 200


@ride_bp.route("/request", methods=["POST"])
@jwt_required()
@student_required
def request_seat():
    """Student requests a seat to a specific stop (zone) on a driver's active route."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    driver_id = data.get("driver_id")
    zone_id = data.get("zone_id")
    pickup_lat = data.get("pickup_lat")
    pickup_lng = data.get("pickup_lng")
    payment_method = data.get("payment_method", "wallet") # "wallet" or "paystack"

    driver = Driver.query.get(driver_id)
    if not driver or driver.status != DriverStatus.APPROVED or not driver.is_online:
        return jsonify({"error": "Driver unavailable"}), 404
    if not driver.active_route_id:
        return jsonify({"error": "Driver has no active route"}), 400
    if driver.seats_available() <= 0:
        return jsonify({"error": "No seats available"}), 409

    stop = RouteStop.query.filter_by(route_id=driver.active_route_id, zone_id=zone_id).first()
    if not stop:
        return jsonify({"error": "That stop is not on this driver's route"}), 400

    existing = RideRequest.query.filter_by(student_id=user_id, driver_id=driver_id).filter(
        RideRequest.status.in_([RideRequestStatus.PENDING_PAYMENT, RideRequestStatus.PENDING, RideRequestStatus.ACCEPTED, RideRequestStatus.ONGOING])
    ).first()
    if existing:
        return jsonify({"error": "You already have an active request with this driver"}), 409

    price = stop.zone.price
    import uuid
    payment_reference = f"ride_{uuid.uuid4().hex}"
    
    if payment_method == "wallet":
        try:
            from app.services.payment.wallet_service import WalletService
            WalletService.hold_funds_for_ride(user_id, price, payment_reference)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    ride_req = RideRequest(
        student_id=user_id,
        driver_id=driver_id,
        route_id=driver.active_route_id,
        zone_id=zone_id,
        pickup_lat=pickup_lat,
        pickup_lng=pickup_lng,
        price=price,
        payment_reference=payment_reference,
        status=RideRequestStatus.PENDING if payment_method == "wallet" else RideRequestStatus.PENDING_PAYMENT,
    )
    db.session.add(ride_req)
    db.session.commit()
    
    if payment_method == "paystack":
        from app.services.payment.paystack_provider import PaystackProvider
        from app.models import Payment, PaymentStatus
        provider = PaystackProvider()
        pay_reference = f"pay_{uuid.uuid4().hex}"
        try:
            user = User.query.get(user_id)
            result = provider.initialize_payment(email=user.email, amount=price, reference=pay_reference)
            
            payment = Payment(
                user_id=user_id,
                amount=price,
                provider="paystack",
                provider_reference=pay_reference,
                purpose="ride_payment",
                meta_data={"ride_request_id": ride_req.id, "payment_reference": payment_reference}
            )
            db.session.add(payment)
            db.session.commit()
            
            return jsonify({"message": "Payment required", "ride_request": ride_req.to_dict(), "payment": result}), 201
        except Exception as e:
            db.session.delete(ride_req)
            db.session.commit()
            return jsonify({"error": str(e)}), 500

    socketio.emit("new_ride_request", enrich_ride_request(ride_req, driver), namespace="/rides",
                   room=f"driver_{driver.id}")
    return jsonify({"message": "Seat requested", "ride_request": ride_req.to_dict()}), 201


@ride_bp.route("/my-requests", methods=["GET"])
@jwt_required()
@student_required
def my_requests():
    user_id = int(get_jwt_identity())
    status_filter = request.args.get("status")
    q = RideRequest.query.filter_by(student_id=user_id)
    if status_filter:
        q = q.filter_by(status=RideRequestStatus(status_filter))
    requests = q.order_by(RideRequest.requested_at.desc()).all()
    return jsonify([enrich_ride_request(r) for r in requests]), 200


@ride_bp.route("/requests/<int:request_id>/cancel", methods=["POST"])
@jwt_required()
@student_required
def cancel_request(request_id):
    user_id = int(get_jwt_identity())
    ride_req = RideRequest.query.filter_by(id=request_id, student_id=user_id).first()
    if not ride_req:
        return jsonify({"error": "Request not found"}), 404
    if ride_req.status not in (RideRequestStatus.PENDING, RideRequestStatus.ACCEPTED, RideRequestStatus.PENDING_PAYMENT):
        return jsonify({"error": "Cannot cancel at this stage"}), 409

    if ride_req.status in (RideRequestStatus.PENDING, RideRequestStatus.ACCEPTED) and ride_req.payment_reference:
        try:
            from app.services.payment.wallet_service import WalletService
            WalletService.refund_ride_payment(user_id, ride_req.price, ride_req.payment_reference)
        except Exception as e:
            pass # Or log it. In a real app we'd queue a retry. For now, we swallow to allow cancel to proceed or fail it. Let's return error.
            return jsonify({"error": f"Refund failed: {e}"}), 500

    ride_req.status = RideRequestStatus.CANCELLED
    db.session.commit()
    socketio.emit("ride_request_update", ride_req.to_dict(), namespace="/rides",
                   room=f"driver_{ride_req.driver_id}")
    return jsonify({"ride_request": ride_req.to_dict()}), 200


@ride_bp.route("/zones", methods=["GET"])
@jwt_required()
def list_zones():
    zones = Zone.query.filter_by(is_active=True).all()
    return jsonify([z.to_dict() for z in zones]), 200
