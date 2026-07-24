from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import DeviceToken, NotificationLog

notification_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@notification_bp.route("/register-device", methods=["POST"])
@jwt_required()
def register_device():
    """Registers (or refreshes) an FCM device token for push notifications."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "token is required"}), 400

    existing = DeviceToken.query.filter_by(token=token).first()
    if existing:
        existing.user_id = user_id
        existing.platform = data.get("platform", existing.platform)
        existing.is_active = True
    else:
        existing = DeviceToken(
            user_id=user_id, token=token, platform=data.get("platform", "web")
        )
        db.session.add(existing)
    db.session.commit()
    return jsonify({"message": "Device registered"}), 200


@notification_bp.route("/unregister-device", methods=["POST"])
@jwt_required()
def unregister_device():
    data = request.get_json() or {}
    token = data.get("token")
    device = DeviceToken.query.filter_by(token=token).first()
    if device:
        device.is_active = False
        db.session.commit()
    return jsonify({"message": "Device unregistered"}), 200


@notification_bp.route("", methods=["GET"])
@jwt_required()
def list_notifications():
    user_id = int(get_jwt_identity())
    limit = request.args.get("limit", default=30, type=int)
    notifications = NotificationLog.query.filter_by(user_id=user_id) \
        .order_by(NotificationLog.created_at.desc()).limit(limit).all()
    return jsonify([n.to_dict() for n in notifications]), 200
