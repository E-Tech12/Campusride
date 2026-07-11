from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models import User, UserRole


def get_current_user():
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


def role_required(*roles):
    """Restrict an endpoint to one or more roles. roles are UserRole enum members."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user:
                return jsonify({"error": "User not found"}), 404
            if user.role not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    return role_required(UserRole.ADMIN)(fn)


def driver_required(fn):
    return role_required(UserRole.DRIVER)(fn)


def student_required(fn):
    return role_required(UserRole.STUDENT)(fn)
