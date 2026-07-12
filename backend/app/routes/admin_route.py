from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app.extensions import db
from app.models import (
    User, UserRole, Driver, DriverStatus, Zone, RideRequest, RideRequestStatus,
    WalletTransaction, TransactionType, TransactionStatus,
    WithdrawalRequest, WithdrawalStatus,
)
from app.utils.decorators import admin_required
from app.services.payment.wallet_service import WalletService

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/public-stats", methods=["GET"])
def public_stats():
    """Non-sensitive aggregate counts for the public landing page. No auth
    required and nothing here (revenue, names, emails) is sensitive -- this
    exists so the landing page can show real numbers instead of hardcoded
    marketing copy like "500+ riders"."""
    return jsonify({
        "total_students": User.query.filter_by(role=UserRole.STUDENT).count(),
        "total_drivers": Driver.query.filter_by(status=DriverStatus.APPROVED).count(),
        "completed_rides": RideRequest.query.filter_by(status=RideRequestStatus.COMPLETED).count(),
    }), 200


@admin_bp.route("/drivers", methods=["GET"])
@jwt_required()
@admin_required
def list_drivers():
    status_filter = request.args.get("status")
    q = Driver.query
    if status_filter:
        q = q.filter_by(status=DriverStatus(status_filter))
    drivers = q.order_by(Driver.created_at.desc()).all()
    return jsonify([d.to_dict() for d in drivers]), 200


@admin_bp.route("/drivers/<int:driver_id>/approve", methods=["POST"])
@jwt_required()
@admin_required
def approve_driver(driver_id):
    admin_id = int(get_jwt_identity())
    driver = Driver.query.get(driver_id)
    if not driver:
        return jsonify({"error": "Driver not found"}), 404

    driver.status = DriverStatus.APPROVED
    driver.approved_by = admin_id
    driver.approved_at = datetime.utcnow()
    driver.rejection_reason = None

    user = User.query.get(driver.user_id)
    user.role = UserRole.DRIVER

    db.session.commit()
    return jsonify({"message": "Driver approved", "driver": driver.to_dict()}), 200


@admin_bp.route("/drivers/<int:driver_id>/reject", methods=["POST"])
@jwt_required()
@admin_required
def reject_driver(driver_id):
    admin_id = int(get_jwt_identity())
    driver = Driver.query.get(driver_id)
    if not driver:
        return jsonify({"error": "Driver not found"}), 404

    data = request.get_json() or {}
    driver.status = DriverStatus.REJECTED
    driver.approved_by = admin_id
    driver.approved_at = datetime.utcnow()
    driver.rejection_reason = data.get("reason", "Not specified")
    db.session.commit()
    return jsonify({"message": "Driver rejected", "driver": driver.to_dict()}), 200


@admin_bp.route("/drivers/<int:driver_id>/suspend", methods=["POST"])
@jwt_required()
@admin_required
def suspend_driver(driver_id):
    driver = Driver.query.get(driver_id)
    if not driver:
        return jsonify({"error": "Driver not found"}), 404
    driver.status = DriverStatus.SUSPENDED
    driver.is_online = False
    db.session.commit()
    return jsonify({"message": "Driver suspended", "driver": driver.to_dict()}), 200


@admin_bp.route("/zones", methods=["GET"])
@jwt_required()
@admin_required
def list_zones():
    zones = Zone.query.order_by(Zone.name).all()
    return jsonify([z.to_dict() for z in zones]), 200


@admin_bp.route("/zones", methods=["POST"])
@jwt_required()
@admin_required
def create_zone():
    data = request.get_json() or {}
    if not data.get("name") or data.get("price") is None:
        return jsonify({"error": "name and price are required"}), 400
    if Zone.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "Zone already exists"}), 409

    zone = Zone(
        name=data["name"],
        price=float(data["price"]),
        lat=data.get("lat"),
        lng=data.get("lng"),
    )
    db.session.add(zone)
    db.session.commit()
    return jsonify({"message": "Zone created", "zone": zone.to_dict()}), 201


@admin_bp.route("/students", methods=["GET"])
@jwt_required()
@admin_required
def get_students():
    """Returns a list of all registered students."""
    students = User.query.filter_by(role=UserRole.STUDENT).all()
    return jsonify([s.to_dict() for s in students]), 200


@admin_bp.route("/zones/<int:zone_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_zone(zone_id):
    zone = Zone.query.get(zone_id)
    if not zone:
        return jsonify({"error": "Zone not found"}), 404
    data = request.get_json() or {}
    if "name" in data:
        zone.name = data["name"]
    if "price" in data:
        zone.price = float(data["price"])
    if "lat" in data:
        zone.lat = data["lat"]
    if "lng" in data:
        zone.lng = data["lng"]
    if "is_active" in data:
        zone.is_active = data["is_active"]
    db.session.commit()
    return jsonify({"message": "Zone updated", "zone": zone.to_dict()}), 200


@admin_bp.route("/zones/<int:zone_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_zone(zone_id):
    zone = Zone.query.get(zone_id)
    if not zone:
        return jsonify({"error": "Zone not found"}), 404
    db.session.delete(zone)
    db.session.commit()
    return jsonify({"message": "Zone deleted"}), 200


@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
@admin_required
def stats():
    total_revenue = db.session.query(func.sum(WalletTransaction.amount)).filter(
        WalletTransaction.transaction_type == TransactionType.PLATFORM_COMMISSION,
        WalletTransaction.status == TransactionStatus.SUCCESS,
    ).scalar() or 0

    return jsonify({
        "total_users": User.query.count(),
        "total_students": User.query.filter_by(role=UserRole.STUDENT).count(),
        "total_drivers": Driver.query.filter_by(status=DriverStatus.APPROVED).count(),
        "pending_driver_applications": Driver.query.filter_by(status=DriverStatus.PENDING).count(),
        "drivers_online": Driver.query.filter_by(status=DriverStatus.APPROVED, is_online=True).count(),
        "total_rides": RideRequest.query.count(),
        "active_rides": RideRequest.query.filter(
            RideRequest.status.in_([RideRequestStatus.ACCEPTED, RideRequestStatus.ONGOING])
        ).count(),
        "completed_rides": RideRequest.query.filter_by(status=RideRequestStatus.COMPLETED).count(),
        "platform_revenue": round(total_revenue, 2),
        "pending_withdrawals": WithdrawalRequest.query.filter_by(status=WithdrawalStatus.PENDING).count(),
    }), 200


@admin_bp.route("/finance", methods=["GET"])
@jwt_required()
@admin_required
def finance():
    """Real revenue/payout figures for the finance dashboard -- replaces what
    was previously a hardcoded chart on the frontend."""
    total_revenue = db.session.query(func.sum(WalletTransaction.amount)).filter(
        WalletTransaction.transaction_type == TransactionType.PLATFORM_COMMISSION,
        WalletTransaction.status == TransactionStatus.SUCCESS,
    ).scalar() or 0
    total_payouts = db.session.query(func.sum(WalletTransaction.amount)).filter(
        WalletTransaction.transaction_type == TransactionType.DRIVER_EARNING,
        WalletTransaction.status == TransactionStatus.SUCCESS,
    ).scalar() or 0

    pending = WithdrawalRequest.query.filter_by(status=WithdrawalStatus.PENDING).all()
    pending_amount = sum(w.amount for w in pending)

    today = datetime.utcnow().date()
    trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        day_sum = db.session.query(func.sum(WalletTransaction.amount)).filter(
            WalletTransaction.transaction_type == TransactionType.PLATFORM_COMMISSION,
            WalletTransaction.status == TransactionStatus.SUCCESS,
            WalletTransaction.completed_at >= day_start,
            WalletTransaction.completed_at < day_end,
        ).scalar() or 0
        trend.append({"date": day.isoformat(), "label": day.strftime("%a"), "revenue": round(day_sum, 2)})

    return jsonify({
        "total_platform_revenue": round(total_revenue, 2),
        "total_driver_payouts": round(total_payouts, 2),
        "pending_withdrawals_count": len(pending),
        "pending_withdrawals_amount": round(pending_amount, 2),
        "revenue_trend": trend,
        "revenue_split": {
            "driver_share": round(total_payouts, 2),
            "platform_share": round(total_revenue, 2),
        },
    }), 200


@admin_bp.route("/withdrawals", methods=["GET"])
@jwt_required()
@admin_required
def list_withdrawals():
    status_filter = request.args.get("status")
    q = WithdrawalRequest.query
    if status_filter:
        q = q.filter_by(status=WithdrawalStatus(status_filter))
    withdrawals = q.order_by(WithdrawalRequest.created_at.desc()).all()
    return jsonify([w.to_dict() for w in withdrawals]), 200


@admin_bp.route("/withdrawals/<int:withdrawal_id>/approve", methods=["POST"])
@jwt_required()
@admin_required
def approve_withdrawal(withdrawal_id):
    w = WithdrawalRequest.query.get(withdrawal_id)
    if not w or w.status != WithdrawalStatus.PENDING:
        return jsonify({"error": "Withdrawal not found or already processed"}), 404

    w.status = WithdrawalStatus.APPROVED
    w.processed_at = datetime.utcnow()
    txn = WalletTransaction.query.filter_by(reference=w.reference).first()
    if txn:
        txn.status = TransactionStatus.SUCCESS
        txn.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Withdrawal approved", "withdrawal": w.to_dict()}), 200


@admin_bp.route("/withdrawals/<int:withdrawal_id>/reject", methods=["POST"])
@jwt_required()
@admin_required
def reject_withdrawal(withdrawal_id):
    w = WithdrawalRequest.query.get(withdrawal_id)
    if not w or w.status != WithdrawalStatus.PENDING:
        return jsonify({"error": "Withdrawal not found or already processed"}), 404

    driver = Driver.query.get(w.driver_id)
    wallet = WalletService.get_or_create_wallet(driver.user_id)
    wallet.balance += w.amount  # refund the held amount back to the driver

    w.status = WithdrawalStatus.REJECTED
    w.processed_at = datetime.utcnow()
    txn = WalletTransaction.query.filter_by(reference=w.reference).first()
    if txn:
        txn.status = TransactionStatus.FAILED
        txn.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Withdrawal rejected", "withdrawal": w.to_dict()}), 200
