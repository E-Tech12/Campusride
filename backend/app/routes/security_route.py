from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db, limiter
from app.models import User, SecurityLog, SecurityEventType
from app.services import security_service as sec

security_bp = Blueprint("security", __name__, url_prefix="/api/security")


@security_bp.route("/change-password/request-otp", methods=["POST"])
@jwt_required()
@limiter.limit("5 per hour")
def request_password_change_otp():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json() or {}
    if not user.check_password(data.get("current_password", "")):
        return jsonify({"error": "Current password is incorrect"}), 401

    error = sec.request_high_risk_otp(user, "password_change")
    if error:
        return jsonify({"error": error}), 429
    return jsonify({"message": "Verification code sent to your email"}), 200


@security_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json() or {}

    if not user.check_password(data.get("current_password", "")):
        return jsonify({"error": "Current password is incorrect"}), 401

    new_password = data.get("new_password")
    if not new_password or len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    error = sec.verify_high_risk_otp(user, "password_change", data.get("otp_code"))
    if error:
        return jsonify({"error": error}), 400

    user.set_password(new_password)
    user.password_changed_at = datetime.utcnow()
    db.session.commit()

    SecurityLog.record(user.id, SecurityEventType.PASSWORD_CHANGED, description="Password changed by user",
                        ip_address=sec.get_request_ip(request))
    db.session.commit()

    sec.revoke_all_sessions(user, reason="Password changed")
    sec.lock_withdrawals(user, reason="Password changed")

    from app.services.notification_service import notify
    from app.models import NotificationEvent
    notify(user.id, NotificationEvent.PASSWORD_CHANGED)

    return jsonify({"message": "Password changed. Please log in again."}), 200


@security_bp.route("/change-email/request-otp", methods=["POST"])
@jwt_required()
@limiter.limit("5 per hour")
def request_email_change_otp():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json() or {}
    new_email = data.get("new_email")
    if not new_email:
        return jsonify({"error": "new_email is required"}), 400
    if User.query.filter_by(email=new_email).first():
        return jsonify({"error": "Email already in use"}), 409

    error = sec.request_high_risk_otp(user, "email_change")
    if error:
        return jsonify({"error": error}), 429
    return jsonify({"message": "Verification code sent to your current email"}), 200


@security_bp.route("/change-email", methods=["POST"])
@jwt_required()
def change_email():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json() or {}
    new_email = data.get("new_email")
    if not new_email:
        return jsonify({"error": "new_email is required"}), 400
    if User.query.filter_by(email=new_email).first():
        return jsonify({"error": "Email already in use"}), 409

    error = sec.verify_high_risk_otp(user, "email_change", data.get("otp_code"))
    if error:
        return jsonify({"error": error}), 400

    old_email = user.email
    user.email = new_email
    user.is_verified = False  # must re-verify the new address
    db.session.commit()

    SecurityLog.record(user.id, SecurityEventType.EMAIL_CHANGED,
                        description=f"Email changed from {old_email} to {new_email}",
                        ip_address=sec.get_request_ip(request))
    db.session.commit()

    sec.revoke_all_sessions(user, reason="Email changed")
    sec.lock_withdrawals(user, reason="Email changed")

    from app.models import OTP
    from datetime import timedelta
    from app.utils.email import send_otp_email
    otp_code = OTP.generate_otp()
    otp = OTP(user_id=user.id, email=new_email, otp_code=otp_code, purpose="email_verification",
              expires_at=datetime.utcnow() + timedelta(minutes=10))
    db.session.add(otp)
    db.session.commit()
    try:
        send_otp_email(email=new_email, otp_code=otp_code, purpose="email_verification")
    except Exception:
        pass

    return jsonify({"message": "Email changed. Please verify your new email and log in again."}), 200


@security_bp.route("/change-phone/request-otp", methods=["POST"])
@jwt_required()
@limiter.limit("5 per hour")
def request_phone_change_otp():
    user = User.query.get(int(get_jwt_identity()))
    error = sec.request_high_risk_otp(user, "phone_change")
    if error:
        return jsonify({"error": error}), 429
    return jsonify({"message": "Verification code sent to your email"}), 200


@security_bp.route("/change-phone", methods=["POST"])
@jwt_required()
def change_phone():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json() or {}
    new_phone = data.get("new_phone")
    if not new_phone:
        return jsonify({"error": "new_phone is required"}), 400

    error = sec.verify_high_risk_otp(user, "phone_change", data.get("otp_code"))
    if error:
        return jsonify({"error": error}), 400

    old_phone = user.phone
    user.phone = new_phone
    db.session.commit()

    SecurityLog.record(user.id, SecurityEventType.PHONE_CHANGED,
                        description=f"Phone changed from {old_phone} to {new_phone}",
                        ip_address=sec.get_request_ip(request))
    db.session.commit()

    sec.lock_withdrawals(user, reason="Phone number changed")
    return jsonify({"message": "Phone number updated", "user": user.to_dict()}), 200


@security_bp.route("/login-history", methods=["GET"])
@jwt_required()
def my_login_history():
    """Lets a user see their own recent login/device activity."""
    user_id = int(get_jwt_identity())
    from app.models import LoginSecurity
    entries = LoginSecurity.query.filter_by(user_id=user_id) \
        .order_by(LoginSecurity.created_at.desc()).limit(20).all()
    return jsonify([e.to_dict() for e in entries]), 200
