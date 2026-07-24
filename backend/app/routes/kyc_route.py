from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import User, DriverKYC, KYCStatus, SecurityLog, SecurityEventType
from app.utils.decorators import driver_required, admin_required

kyc_bp = Blueprint("kyc", __name__, url_prefix="/api")


@kyc_bp.route("/driver/kyc", methods=["POST"])
@jwt_required()
@driver_required
def submit_kyc():
    """Driver submits identity documents. Document uploads are expected to
    already be hosted (e.g. via the platform's existing file/object storage)
    and passed here as URLs -- this endpoint records the KYC application and
    puts it into the admin review queue."""
    user = User.query.get(int(get_jwt_identity()))
    driver = user.driver_profile
    if not driver:
        return jsonify({"error": "No driver profile"}), 404

    data = request.get_json() or {}
    required = ["government_id_url", "selfie_url", "drivers_license_url"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    kyc = DriverKYC(
        driver_id=driver.id,
        government_id_url=data["government_id_url"],
        government_id_type=data.get("government_id_type"),
        selfie_url=data["selfie_url"],
        drivers_license_url=data["drivers_license_url"],
        proof_of_ownership_url=data.get("proof_of_ownership_url"),
        status=KYCStatus.PENDING,
    )
    db.session.add(kyc)
    SecurityLog.record(user.id, SecurityEventType.KYC_SUBMITTED, description="Driver KYC submitted")
    db.session.commit()
    return jsonify({"message": "KYC submitted for review", "kyc": kyc.to_dict()}), 201


@kyc_bp.route("/driver/kyc/me", methods=["GET"])
@jwt_required()
@driver_required
def my_kyc():
    user = User.query.get(int(get_jwt_identity()))
    driver = user.driver_profile
    if not driver:
        return jsonify({"error": "No driver profile"}), 404
    latest = DriverKYC.query.filter_by(driver_id=driver.id).order_by(DriverKYC.created_at.desc()).first()
    if not latest:
        return jsonify({"status": None, "kyc": None}), 200
    return jsonify({"status": latest.status.value, "kyc": latest.to_dict()}), 200


@kyc_bp.route("/admin/kyc", methods=["GET"])
@jwt_required()
@admin_required
def list_kyc():
    status_filter = request.args.get("status")
    q = DriverKYC.query
    if status_filter:
        q = q.filter_by(status=KYCStatus(status_filter))
    submissions = q.order_by(DriverKYC.created_at.desc()).all()
    return jsonify([k.to_dict() for k in submissions]), 200


@kyc_bp.route("/admin/kyc/<int:kyc_id>/approve", methods=["POST"])
@jwt_required()
@admin_required
def approve_kyc(kyc_id):
    admin_id = int(get_jwt_identity())
    kyc = DriverKYC.query.get(kyc_id)
    if not kyc:
        return jsonify({"error": "KYC submission not found"}), 404

    kyc.status = KYCStatus.APPROVED
    kyc.reviewed_by = admin_id
    kyc.reviewed_at = datetime.utcnow()
    kyc.rejection_reason = None
    db.session.commit()

    driver_user_id = kyc.driver.user_id
    SecurityLog.record(driver_user_id, SecurityEventType.KYC_APPROVED, description="Driver KYC approved by admin")
    db.session.commit()

    from app.services.notification_service import notify
    from app.models import NotificationEvent
    notify(driver_user_id, NotificationEvent.KYC_APPROVED)

    return jsonify({"message": "KYC approved", "kyc": kyc.to_dict()}), 200


@kyc_bp.route("/admin/kyc/<int:kyc_id>/reject", methods=["POST"])
@jwt_required()
@admin_required
def reject_kyc(kyc_id):
    admin_id = int(get_jwt_identity())
    kyc = DriverKYC.query.get(kyc_id)
    if not kyc:
        return jsonify({"error": "KYC submission not found"}), 404

    data = request.get_json() or {}
    kyc.status = KYCStatus.REJECTED
    kyc.reviewed_by = admin_id
    kyc.reviewed_at = datetime.utcnow()
    kyc.rejection_reason = data.get("reason", "Not specified")
    db.session.commit()

    driver_user_id = kyc.driver.user_id
    SecurityLog.record(driver_user_id, SecurityEventType.KYC_REJECTED,
                        description=f"Driver KYC rejected: {kyc.rejection_reason}")
    db.session.commit()

    from app.services.notification_service import notify
    from app.models import NotificationEvent
    notify(driver_user_id, NotificationEvent.KYC_REJECTED)

    return jsonify({"message": "KYC rejected", "kyc": kyc.to_dict()}), 200
