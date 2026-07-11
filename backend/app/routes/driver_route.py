import uuid
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app.extensions import db, socketio
from app.models import (
    User, UserRole, Driver, DriverStatus, Route, RouteStop, Zone,
    RideRequest, RideRequestStatus,
    Wallet, WalletTransaction, TransactionType, TransactionStatus,
    WithdrawalRequest, WithdrawalStatus,
)
from app.utils.decorators import driver_required
from app.utils.geo import haversine_km, eta_minutes
from app.services.payment.wallet_service import WalletService

driver_bp = Blueprint("driver", __name__, url_prefix="/api/driver")


def _enrich_request(ride_req, driver):
    data = ride_req.to_dict()
    distance = None
    if driver.current_lat is not None and ride_req.pickup_lat is not None:
        distance = haversine_km(driver.current_lat, driver.current_lng, ride_req.pickup_lat, ride_req.pickup_lng)
    data["distance_km"] = round(distance, 2) if distance is not None else None
    data["eta_minutes"] = eta_minutes(distance)
    return data


@driver_bp.route("/apply", methods=["POST"])
@jwt_required()
def apply():
    """Any verified student can apply to become a driver. Goes to PENDING for admin review."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.driver_profile:
        return jsonify({"error": "You already have a driver application", "status": user.driver_profile.status.value}), 409

    data = request.get_json() or {}
    required = ["vehicle_make", "vehicle_model", "vehicle_color", "plate_number", "license_number"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if Driver.query.filter_by(plate_number=data["plate_number"]).first():
        return jsonify({"error": "Plate number already registered"}), 409

    driver = Driver(
        user_id=user.id,
        vehicle_make=data["vehicle_make"],
        vehicle_model=data["vehicle_model"],
        vehicle_color=data["vehicle_color"],
        plate_number=data["plate_number"],
        license_number=data["license_number"],
        seat_capacity=int(data.get("seat_capacity", 4)),
        status=DriverStatus.PENDING,
    )
    db.session.add(driver)
    db.session.commit()
    return jsonify({"message": "Driver application submitted. Awaiting admin approval.", "driver": driver.to_dict()}), 201


@driver_bp.route("/me", methods=["GET"])
@jwt_required()
def my_driver_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.driver_profile:
        return jsonify({"error": "No driver profile found"}), 404
    return jsonify(user.driver_profile.to_dict()), 200


@driver_bp.route("/route", methods=["POST"])
@jwt_required()
@driver_required
def create_route():
    """Create (or replace) the driver's route: a name + ordered list of zone_ids."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    driver = user.driver_profile
    if not driver or driver.status != DriverStatus.APPROVED:
        return jsonify({"error": "Driver not approved"}), 403

    data = request.get_json() or {}
    name = data.get("name")
    zone_ids = data.get("zone_ids")  # ordered list
    if not name or not zone_ids or not isinstance(zone_ids, list):
        return jsonify({"error": "name and zone_ids (ordered list) are required"}), 400

    route = Route(driver_id=driver.id, name=name)
    db.session.add(route)
    db.session.flush()

    for seq, zone_id in enumerate(zone_ids):
        zone = Zone.query.get(zone_id)
        if not zone:
            db.session.rollback()
            return jsonify({"error": f"Zone {zone_id} not found"}), 400
        db.session.add(RouteStop(route_id=route.id, zone_id=zone_id, sequence=seq))

    db.session.commit()
    return jsonify({"message": "Route created", "route": route.to_dict()}), 201


@driver_bp.route("/routes", methods=["GET"])
@jwt_required()
@driver_required
def my_routes():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    driver = user.driver_profile
    if not driver:
        return jsonify({"error": "No driver profile"}), 404
    routes = Route.query.filter_by(driver_id=driver.id).all()
    return jsonify([r.to_dict() for r in routes]), 200


@driver_bp.route("/go-online", methods=["POST"])
@jwt_required()
@driver_required
def go_online():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    driver = user.driver_profile
    if not driver or driver.status != DriverStatus.APPROVED:
        return jsonify({"error": "Driver not approved"}), 403

    data = request.get_json() or {}
    route_id = data.get("route_id")
    lat = data.get("lat")
    lng = data.get("lng")

    if route_id:
        route = Route.query.filter_by(id=route_id, driver_id=driver.id).first()
        if not route:
            return jsonify({"error": "Route not found"}), 404
        driver.active_route_id = route.id

    if not driver.active_route_id:
        return jsonify({"error": "Set an active route before going online"}), 400

    driver.is_online = True
    if lat is not None and lng is not None:
        driver.current_lat = lat
        driver.current_lng = lng
        driver.last_location_update = datetime.utcnow()

    db.session.commit()
    socketio.emit("driver_status_update", driver.to_dict(), namespace="/rides")
    return jsonify({"message": "You are now online", "driver": driver.to_dict()}), 200


@driver_bp.route("/go-offline", methods=["POST"])
@jwt_required()
@driver_required
def go_offline():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    driver = user.driver_profile
    if not driver:
        return jsonify({"error": "No driver profile"}), 404

    driver.is_online = False
    db.session.commit()
    socketio.emit("driver_status_update", driver.to_dict(), namespace="/rides")
    return jsonify({"message": "You are now offline"}), 200


@driver_bp.route("/location", methods=["POST"])
@jwt_required()
@driver_required
def update_location():
    """Polled fallback for live location updates (in addition to socket events)."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    driver = user.driver_profile
    if not driver:
        return jsonify({"error": "No driver profile"}), 404

    data = request.get_json() or {}
    lat, lng = data.get("lat"), data.get("lng")
    if lat is None or lng is None:
        return jsonify({"error": "lat and lng required"}), 400

    driver.current_lat = lat
    driver.current_lng = lng
    driver.last_location_update = datetime.utcnow()
    db.session.commit()

    socketio.emit("driver_location_update", {
        "driver_id": driver.id, "lat": lat, "lng": lng
    }, namespace="/rides")
    return jsonify({"message": "Location updated"}), 200


@driver_bp.route("/requests", methods=["GET"])
@jwt_required()
@driver_required
def incoming_requests():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    driver = user.driver_profile
    if not driver:
        return jsonify({"error": "No driver profile"}), 404

    status_filter = request.args.get("status")
    q = RideRequest.query.filter_by(driver_id=driver.id)
    if status_filter:
        q = q.filter_by(status=RideRequestStatus(status_filter))
    requests = q.order_by(RideRequest.requested_at.desc()).all()
    return jsonify([_enrich_request(r, driver) for r in requests]), 200


@driver_bp.route("/requests/<int:request_id>/respond", methods=["POST"])
@jwt_required()
@driver_required
def respond_to_request(request_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    driver = user.driver_profile
    ride_req = RideRequest.query.filter_by(id=request_id, driver_id=driver.id).first()
    if not ride_req:
        return jsonify({"error": "Request not found"}), 404
    if ride_req.status != RideRequestStatus.PENDING:
        return jsonify({"error": "Request already responded to"}), 409

    decision = (request.get_json() or {}).get("decision")  # "accept" or "reject"
    if decision == "accept":
        if driver.seats_available() <= 0:
            return jsonify({"error": "No seats available"}), 409
        ride_req.status = RideRequestStatus.ACCEPTED
    elif decision == "reject":
        if ride_req.payment_reference:
            from app.services.payment.wallet_service import WalletService
            try:
                WalletService.refund_ride_payment(ride_req.student_id, ride_req.price, ride_req.payment_reference, description="Driver Rejected Ride")
            except Exception as e:
                pass # fail silently if refund fails, or log it
        ride_req.status = RideRequestStatus.REJECTED
    else:
        return jsonify({"error": "decision must be 'accept' or 'reject'"}), 400

    ride_req.responded_at = datetime.utcnow()
    db.session.commit()

    socketio.emit("ride_request_update", ride_req.to_dict(), namespace="/rides",
                   room=f"student_{ride_req.student_id}")
    socketio.emit("driver_status_update", driver.to_dict(), namespace="/rides")
    return jsonify({"message": f"Request {decision}ed", "ride_request": ride_req.to_dict()}), 200


@driver_bp.route("/requests/<int:request_id>/pickup", methods=["POST"])
@jwt_required()
@driver_required
def mark_pickup(request_id):
    user_id = int(get_jwt_identity())
    driver = User.query.get(user_id).driver_profile
    ride_req = RideRequest.query.filter_by(id=request_id, driver_id=driver.id).first()
    if not ride_req or ride_req.status != RideRequestStatus.ACCEPTED:
        return jsonify({"error": "Invalid request state"}), 409
    ride_req.status = RideRequestStatus.ONGOING
    ride_req.picked_up_at = datetime.utcnow()
    db.session.commit()
    socketio.emit("ride_request_update", ride_req.to_dict(), namespace="/rides",
                   room=f"student_{ride_req.student_id}")
    return jsonify({"ride_request": ride_req.to_dict()}), 200


@driver_bp.route("/requests/<int:request_id>/complete", methods=["POST"])
@jwt_required()
@driver_required
def mark_complete(request_id):
    user_id = int(get_jwt_identity())
    driver = User.query.get(user_id).driver_profile
    ride_req = RideRequest.query.filter_by(id=request_id, driver_id=driver.id).first()
    if not ride_req or ride_req.status != RideRequestStatus.ONGOING:
        return jsonify({"error": "Invalid request state"}), 409
        
    if ride_req.payment_reference:
        try:
            from app.services.payment.wallet_service import WalletService
            WalletService.complete_ride_payment(
                student_id=ride_req.student_id,
                driver_user_id=driver.user_id,
                amount=ride_req.price,
                reference=ride_req.payment_reference
            )
        except Exception as e:
            return jsonify({"error": f"Payment completion failed: {e}"}), 500

    ride_req.status = RideRequestStatus.COMPLETED
    ride_req.completed_at = datetime.utcnow()
    db.session.commit()
    socketio.emit("ride_request_update", ride_req.to_dict(), namespace="/rides",
                   room=f"student_{ride_req.student_id}")
    socketio.emit("driver_status_update", driver.to_dict(), namespace="/rides")
    return jsonify({"ride_request": ride_req.to_dict()}), 200


@driver_bp.route("/earnings", methods=["GET"])
@jwt_required()
@driver_required
def earnings():
    """Real earnings/wallet summary for the driver dashboard: today's earnings,
    today's rides, a 7-day earnings chart, recent transactions and pending
    withdrawals -- all computed from actual wallet + ride records."""
    user = User.query.get(int(get_jwt_identity()))
    driver = user.driver_profile
    if not driver:
        return jsonify({"error": "No driver profile"}), 404

    wallet = WalletService.get_or_create_wallet(user.id)

    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())

    today_earnings = db.session.query(func.sum(WalletTransaction.amount)).filter(
        WalletTransaction.wallet_id == wallet.id,
        WalletTransaction.transaction_type == TransactionType.DRIVER_EARNING,
        WalletTransaction.status == TransactionStatus.SUCCESS,
        WalletTransaction.completed_at >= today_start,
    ).scalar() or 0

    today_rides = RideRequest.query.filter(
        RideRequest.driver_id == driver.id,
        RideRequest.status == RideRequestStatus.COMPLETED,
        RideRequest.completed_at >= today_start,
    ).count()

    weekly_chart = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        day_sum = db.session.query(func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.wallet_id == wallet.id,
            WalletTransaction.transaction_type == TransactionType.DRIVER_EARNING,
            WalletTransaction.status == TransactionStatus.SUCCESS,
            WalletTransaction.completed_at >= day_start,
            WalletTransaction.completed_at < day_end,
        ).scalar() or 0
        weekly_chart.append({
            "date": day.isoformat(),
            "label": day.strftime("%a"),
            "earnings": round(day_sum, 2),
        })

    recent_txns = WalletTransaction.query.filter_by(wallet_id=wallet.id) \
        .order_by(WalletTransaction.created_at.desc()).limit(10).all()

    pending_withdrawals = WithdrawalRequest.query.filter_by(
        driver_id=driver.id, status=WithdrawalStatus.PENDING
    ).count()

    total_rides = RideRequest.query.filter_by(
        driver_id=driver.id, status=RideRequestStatus.COMPLETED
    ).count()

    return jsonify({
        "balance": wallet.balance,
        "pending_balance": wallet.pending_balance,
        "today_earnings": round(today_earnings, 2),
        "today_rides": today_rides,
        "total_rides": total_rides,
        "pending_withdrawals": pending_withdrawals,
        "weekly_chart": weekly_chart,
        "recent_transactions": [t.to_dict() for t in recent_txns],
    }), 200


@driver_bp.route("/withdraw", methods=["POST"])
@jwt_required()
@driver_required
def request_withdrawal():
    user = User.query.get(int(get_jwt_identity()))
    driver = user.driver_profile
    if not driver:
        return jsonify({"error": "No driver profile"}), 404

    data = request.get_json() or {}
    amount = data.get("amount")
    if not amount or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    wallet = WalletService.get_or_create_wallet(user.id)
    if amount > wallet.balance:
        return jsonify({"error": "Insufficient balance"}), 400

    reference = f"wd_{uuid.uuid4().hex}"
    wallet.balance -= amount

    withdrawal = WithdrawalRequest(
        driver_id=driver.id,
        amount=amount,
        bank_code=data.get("bank_code"),
        account_number=data.get("account_number"),
        account_name=data.get("account_name"),
        reference=reference,
    )
    txn = WalletTransaction(
        wallet_id=wallet.id,
        amount=-amount,
        transaction_type=TransactionType.WITHDRAWAL,
        status=TransactionStatus.PENDING,
        reference=reference,
        description="Withdrawal request pending admin approval",
    )
    db.session.add(withdrawal)
    db.session.add(txn)
    db.session.commit()
    return jsonify({"message": "Withdrawal requested", "withdrawal": withdrawal.to_dict()}), 201


@driver_bp.route("/withdrawals", methods=["GET"])
@jwt_required()
@driver_required
def my_withdrawals():
    user = User.query.get(int(get_jwt_identity()))
    driver = user.driver_profile
    if not driver:
        return jsonify({"error": "No driver profile"}), 404
    withdrawals = WithdrawalRequest.query.filter_by(driver_id=driver.id) \
        .order_by(WithdrawalRequest.created_at.desc()).all()
    return jsonify([w.to_dict() for w in withdrawals]), 200
