from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.extensions import db, limiter
from app.models import User, UserRole, OTP, PasswordResetToken, SecurityLog, SecurityEventType
from app.utils.email import send_otp_email
from app.services import security_service as sec

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    role = data.get("role", "student")
    
    if role == "student":
        required = ["email", "username", "full_name", "student_id", "password"]
    else:
        required = ["email", "username", "full_name", "password", "license_number", "vehicle_make", "vehicle_model", "plate_number"]
        
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already taken"}), 409
    if role == "student" and User.query.filter_by(student_id=data["student_id"]).first():
        return jsonify({"error": "Student ID already registered"}), 409

    user = User(
        email=data["email"],
        username=data["username"],
        full_name=data["full_name"],
        student_id=data.get("student_id") if role == "student" else None,
        phone=data.get("phone"),
        role=UserRole.STUDENT if role == "student" else UserRole.DRIVER,
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    
    if role == "driver":
        from app.models import Driver, DriverStatus
        driver_profile = Driver(
            user_id=user.id,
            license_number=data["license_number"],
            vehicle_make=data["vehicle_make"],
            vehicle_model=data["vehicle_model"],
            vehicle_color=data.get("vehicle_color", "Unknown"),
            plate_number=data["plate_number"],
            seat_capacity=data.get("seat_capacity", 4),
            status=DriverStatus.PENDING
        )
        db.session.add(driver_profile)
        db.session.commit()

    otp_code = OTP.generate_otp()
    otp = OTP(
        user_id=user.id,
        email=user.email,
        otp_code=otp_code,
        purpose="email_verification",
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.session.add(otp)
    db.session.commit()
    try:
        send_otp_email(
            email=user.email,
            otp_code=otp_code,
            purpose="email_verification"
        )
    except Exception as e:
        print("RESEND ERROR:", str(e))
    return jsonify({"message": "Registered. Check your email for a verification code.", "user_id": user.id}), 201


@auth_bp.route("/verify-email", methods=["POST"])
def verify_email():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email")).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp = (
        OTP.query.filter_by(user_id=user.id, purpose="email_verification", otp_code=data.get("otp_code"))
        .order_by(OTP.created_at.desc())
        .first()
    )
    if not otp or not otp.is_valid():
        return jsonify({"error": "Invalid or expired code"}), 400

    otp.use()
    user.is_verified = True
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"message": "Email verified", "access_token": token, "user": user.to_dict()}), 200


@auth_bp.route("/resend-otp", methods=["POST"])
@limiter.limit("10 per hour")
def resend_otp():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email")).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    velocity_error = sec.check_otp_velocity(user, data.get("purpose", "email_verification"))
    if velocity_error:
        return jsonify({"error": velocity_error}), 429

    otp_code = OTP.generate_otp()
    otp = OTP(
        user_id=user.id,
        email=user.email,
        otp_code=otp_code,
        purpose=data.get("purpose", "email_verification"),
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.session.add(otp)
    db.session.commit()
    try:
        send_otp_email(
        email=user.email,
        otp_code=otp_code,
        purpose=otp.purpose
    )
    except Exception as e:
        print("RESEND ERROR:", str(e))
    return jsonify({"message": "OTP resent"}), 200


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.get_json() or {}
    identifier = data.get("email") or data.get("username")
    password = data.get("password")
    if not identifier or not password:
        return jsonify({"error": "Email/username and password required"}), 400

    user = User.query.filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()

    # Account lockout check happens before password comparison so a locked
    # account can't be probed indefinitely while "locked".
    if user:
        lockout_error = sec.check_account_lockout(user)
        if lockout_error:
            return jsonify({"error": lockout_error}), 423

    if not user or not user.check_password(password):
        if user:
            sec.register_failed_login(user, ip_address=sec.get_request_ip(request),
                                       user_agent=request.headers.get("User-Agent", ""))
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.account_active:
        return jsonify({"error": "Account is deactivated"}), 403

    if not user.is_verified:
        return jsonify({"error": "Email not verified", "needs_verification": True}), 403

    sec.reset_failed_login(user)

    login_entry = sec.record_login(user, request, successful=True)

    if sec.login_requires_step_up_otp(login_entry):
        # New device + new location (or high risk score): require OTP before
        # issuing a token, even though the password was correct.
        error = sec.request_high_risk_otp(user, "login_verify")
        if error:
            return jsonify({"error": error}), 429

        from app.services.notification_service import notify
        from app.models import NotificationEvent
        notify(user.id, NotificationEvent.SUSPICIOUS_LOGIN, data={"ip": login_entry.ip_address})

        return jsonify({
            "message": "New device/location detected. Enter the verification code sent to your email.",
            "needs_login_otp": True,
            "user_id": user.id,
        }), 200

    user.last_login = datetime.utcnow()
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()}), 200


@auth_bp.route("/login/verify-otp", methods=["POST"])
@limiter.limit("10 per minute")
def login_verify_otp():
    """Completes a step-up-verified login: the password was already correct,
    this just confirms the OTP sent to email for the new device/location."""
    data = request.get_json() or {}
    user = User.query.get(data.get("user_id")) if data.get("user_id") else None
    if not user:
        return jsonify({"error": "Invalid request"}), 400

    error = sec.verify_high_risk_otp(user, "login_verify", data.get("otp_code"))
    if error:
        return jsonify({"error": error}), 400

    user.last_login = datetime.utcnow()
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()}), 200


@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("10 per hour")
def forgot_password():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email")).first()
    if not user:
        # Don't leak whether the email exists
        return jsonify({"message": "If that email exists, a reset code has been sent"}), 200

    velocity_error = sec.check_otp_velocity(user, "password_reset")
    if velocity_error:
        # Still return the generic message to avoid leaking account existence/state.
        return jsonify({"message": "If that email exists, a reset code has been sent"}), 200

    otp_code = OTP.generate_otp()
    otp = OTP(
        user_id=user.id,
        email=user.email,
        otp_code=otp_code,
        purpose="password_reset",
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.session.add(otp)
    db.session.commit()
    try:
        send_otp_email(
            email=user.email,
            otp_code=otp_code,
            purpose="password_reset"
        )
    except Exception as e:
        print("RESEND ERROR:", str(e))
    return jsonify({"message": "If that email exists, a reset code has been sent"}), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email")).first()
    if not user:
        return jsonify({"error": "Invalid request"}), 400

    otp = (
        OTP.query.filter_by(user_id=user.id, purpose="password_reset", otp_code=data.get("otp_code"))
        .order_by(OTP.created_at.desc())
        .first()
    )
    if not otp or not otp.is_valid():
        return jsonify({"error": "Invalid or expired code"}), 400

    new_password = data.get("new_password")
    if not new_password or len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    otp.use()
    user.set_password(new_password)
    user.password_changed_at = datetime.utcnow()
    db.session.commit()

    SecurityLog.record(user.id, SecurityEventType.PASSWORD_RESET, description="Password reset via OTP",
                        ip_address=sec.get_request_ip(request))
    db.session.commit()

    sec.revoke_all_sessions(user, reason="Password reset")
    sec.lock_withdrawals(user, reason="Password reset")

    return jsonify({"message": "Password reset successfully. Please log in again."}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = user.to_dict()
    if user.driver_profile:
        data["driver_profile"] = user.driver_profile.to_dict()
    return jsonify(data), 200
