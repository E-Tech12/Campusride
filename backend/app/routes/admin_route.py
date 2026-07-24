from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app.extensions import db
from app.models import (
    User, UserRole, Driver, DriverStatus, Zone, RideRequest, RideRequestStatus,
    WalletTransaction, TransactionType, TransactionStatus,
    WithdrawalRequest, WithdrawalStatus,
    SecurityLog, SecurityEventType, LoginSecurity,
    FraudAlert, FraudAlertStatus,
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

    user = User.query.get(driver.user_id)
    from app.services.payment.wallet_service import WalletService
    wallet = WalletService.get_or_create_wallet(user.id)
    if wallet.balance > 0 or wallet.pending_balance > 0:
        return jsonify({"error": "Please withdraw or use your wallet balance before becoming a driver."}), 400

    driver.status = DriverStatus.APPROVED
    driver.approved_by = admin_id
    driver.approved_at = datetime.utcnow()
    driver.rejection_reason = None

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
    if not w:
        return jsonify({"error": "Withdrawal not found"}), 404
    if w.status != WithdrawalStatus.PENDING:
        return jsonify({"error": "Withdrawal already processed"}), 409
    if not w.bank_verified:
        return jsonify({"error": "Bank account verification is required before approval."}), 400

    w.status = WithdrawalStatus.APPROVED
    w.processed_at = datetime.utcnow()
    txn = WalletTransaction.query.filter_by(reference=w.reference).first()
    if txn:
        txn.status = TransactionStatus.SUCCESS
        txn.completed_at = datetime.utcnow()
    db.session.commit()

    driver = Driver.query.get(w.driver_id)
    from app.services.notification_service import notify
    from app.models import NotificationEvent
    notify(driver.user_id, NotificationEvent.WITHDRAWAL_APPROVED, data={"amount": w.amount})

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

    from app.services.notification_service import notify
    from app.models import NotificationEvent
    notify(driver.user_id, NotificationEvent.WITHDRAWAL_FAILED, data={"amount": w.amount})

    return jsonify({"message": "Withdrawal rejected", "withdrawal": w.to_dict()}), 200


# ---------------------------------------------------------------------------
# Phase 8: expanded admin security dashboard
# ---------------------------------------------------------------------------
@admin_bp.route("/security/logs", methods=["GET"])
@jwt_required()
@admin_required
def security_logs():
    event_filter = request.args.get("event_type")
    user_id_filter = request.args.get("user_id", type=int)
    limit = request.args.get("limit", default=100, type=int)

    q = SecurityLog.query
    if event_filter:
        q = q.filter_by(event_type=SecurityEventType(event_filter))
    if user_id_filter:
        q = q.filter_by(user_id=user_id_filter)
    logs = q.order_by(SecurityLog.created_at.desc()).limit(limit).all()
    return jsonify([l.to_dict() for l in logs]), 200


@admin_bp.route("/security/logins", methods=["GET"])
@jwt_required()
@admin_required
def suspicious_logins():
    """New-device / new-location logins, most recent first."""
    limit = request.args.get("limit", default=100, type=int)
    logins = LoginSecurity.query.filter(
        (LoginSecurity.is_new_device == True) | (LoginSecurity.is_new_location == True)  # noqa: E712
    ).order_by(LoginSecurity.created_at.desc()).limit(limit).all()
    return jsonify([l.to_dict() for l in logins]), 200


@admin_bp.route("/security/devices/<int:user_id>", methods=["GET"])
@jwt_required()
@admin_required
def device_history(user_id):
    logins = LoginSecurity.query.filter_by(user_id=user_id) \
        .order_by(LoginSecurity.created_at.desc()).limit(50).all()
    return jsonify([l.to_dict() for l in logins]), 200


@admin_bp.route("/security/locked-accounts", methods=["GET"])
@jwt_required()
@admin_required
def locked_accounts():
    users = User.query.filter(User.locked_until.isnot(None)).all()
    locked = [u.to_admin_dict() for u in users if u.is_locked()]
    return jsonify(locked), 200


@admin_bp.route("/security/accounts/<int:user_id>/unlock", methods=["POST"])
@jwt_required()
@admin_required
def unlock_account(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.locked_until = None
    user.failed_login_attempts = 0
    db.session.commit()
    SecurityLog.record(user.id, SecurityEventType.ACCOUNT_UNLOCKED, description="Unlocked by admin")
    db.session.commit()
    return jsonify({"message": "Account unlocked"}), 200


@admin_bp.route("/security/otp-failures", methods=["GET"])
@jwt_required()
@admin_required
def otp_failures():
    limit = request.args.get("limit", default=100, type=int)
    logs = SecurityLog.query.filter_by(event_type=SecurityEventType.OTP_FAILED) \
        .order_by(SecurityLog.created_at.desc()).limit(limit).all()
    return jsonify([l.to_dict() for l in logs]), 200


@admin_bp.route("/security/withdrawal-attempts", methods=["GET"])
@jwt_required()
@admin_required
def withdrawal_attempts():
    """Includes both successful requests and blocked attempts (lock/limit/velocity)."""
    limit = request.args.get("limit", default=100, type=int)
    blocked_events = [
        SecurityEventType.WITHDRAWAL_BLOCKED_LOCK,
        SecurityEventType.WITHDRAWAL_BLOCKED_LIMIT,
        SecurityEventType.WITHDRAWAL_BLOCKED_VELOCITY,
        SecurityEventType.WITHDRAWAL_REQUESTED,
    ]
    logs = SecurityLog.query.filter(SecurityLog.event_type.in_(blocked_events)) \
        .order_by(SecurityLog.created_at.desc()).limit(limit).all()
    return jsonify([l.to_dict() for l in logs]), 200


@admin_bp.route("/fraud-alerts", methods=["GET"])
@jwt_required()
@admin_required
def list_fraud_alerts():
    status_filter = request.args.get("status")
    q = FraudAlert.query
    if status_filter:
        q = q.filter_by(status=FraudAlertStatus(status_filter))
    alerts = q.order_by(FraudAlert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts]), 200


@admin_bp.route("/fraud-alerts/<int:alert_id>/resolve", methods=["POST"])
@jwt_required()
@admin_required
def resolve_fraud_alert(alert_id):
    admin_id = int(get_jwt_identity())
    alert = FraudAlert.query.get(alert_id)
    if not alert:
        return jsonify({"error": "Alert not found"}), 404

    data = request.get_json() or {}
    new_status = data.get("status", "resolved")
    alert.status = FraudAlertStatus(new_status)
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = admin_id
    alert.resolution_notes = data.get("notes")
    db.session.commit()
    return jsonify({"message": "Alert updated", "alert": alert.to_dict()}), 200


@admin_bp.route("/disputes", methods=["GET"])
@jwt_required()
@admin_required
def list_disputes():
    disputes = RideRequest.query.filter_by(status=RideRequestStatus.DISPUTED) \
        .order_by(RideRequest.disputed_at.desc()).all()
    return jsonify([d.to_dict() for d in disputes]), 200


@admin_bp.route("/disputes/<int:request_id>/resolve", methods=["POST"])
@jwt_required()
@admin_required
def resolve_dispute(request_id):
    """Admin resolves a disputed ride: either release funds to the driver
    (favor_driver) or refund the student (favor_student)."""
    ride_req = RideRequest.query.get(request_id)
    if not ride_req or ride_req.status != RideRequestStatus.DISPUTED:
        return jsonify({"error": "Ride is not in a disputed state"}), 409

    data = request.get_json() or {}
    resolution = data.get("resolution")  # "favor_driver" or "favor_student"

    if resolution == "favor_driver":
        from app.services import ride_completion_service
        ride_completion_service.confirm_completion(ride_req)
    elif resolution == "favor_student":
        from app.services.payment.wallet_service import WalletService
        if ride_req.payment_reference:
            WalletService.refund_ride_payment(ride_req.student_id, ride_req.price,
                                               ride_req.payment_reference, description="Dispute resolved in rider's favor")
        ride_req.status = RideRequestStatus.CANCELLED
        db.session.commit()
    else:
        return jsonify({"error": "resolution must be 'favor_driver' or 'favor_student'"}), 400

    return jsonify({"message": "Dispute resolved", "ride_request": ride_req.to_dict()}), 200


@admin_bp.route("/payouts", methods=["GET"])
@jwt_required()
@admin_required
def payout_history():
    status_filter = request.args.get("status")
    q = WithdrawalRequest.query
    if status_filter:
        q = q.filter_by(status=WithdrawalStatus(status_filter))
    withdrawals = q.order_by(WithdrawalRequest.created_at.desc()).all()
    return jsonify([w.to_dict() for w in withdrawals]), 200


@admin_bp.route("/cron/auto-release-rides", methods=["POST"])
def cron_auto_release_rides():
    """Intended to be called periodically (e.g. every 5 minutes) by an
    external scheduler/cron -- releases funds for AWAITING_COMPLETION rides
    whose completion_deadline has passed with no student response. Guarded by
    a shared secret rather than a user JWT since this is a machine-to-machine
    call, not a user action."""
    import os
    secret = request.headers.get("X-Cron-Secret")
    if not secret or secret != os.getenv("CRON_SECRET"):
        return jsonify({"error": "Unauthorized"}), 401

    from app.services import ride_completion_service
    released = ride_completion_service.auto_release_overdue_completions()
    return jsonify({"released_ride_ids": released, "count": len(released)}), 200
