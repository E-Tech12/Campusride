import os
from flask import Flask, app, jsonify
from dotenv import load_dotenv

from app.extensions import db, migrate, jwt, cors, socketio, limiter

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    # Required for @jwt.token_in_blocklist_loader to actually be invoked --
    # flask-jwt-extended does not check the blocklist unless this is enabled.
    app.config["JWT_BLOCKLIST_ENABLED"] = True
    app.config["JWT_BLOCKLIST_TOKEN_CHECKS"] = ["access", "refresh"]

    app.config["FRONTEND_URL"] = os.getenv(
            "FRONTEND_URL",
            "http://localhost:5173"
        )
    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    
    cors.init_app(
    app,
    resources={r"/api/*": {"origins": "*"}}
    )
    socketio.init_app(
    app,
    cors_allowed_origins="*"
    )

    # Import models so Alembic can see them
    from app import models  # noqa: F401

    # --- Global session revocation (Phase 1 #2) ---
    # Any JWT issued before a user's tokens_invalidated_at timestamp (set on
    # password change/reset) is rejected here, forcing re-login everywhere.
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        from datetime import datetime, timezone
        from app.models import User

        user_id = jwt_payload.get("sub")
        if user_id is None:
            return False
        user = User.query.get(int(user_id))
        if not user or not user.tokens_invalidated_at:
            return False

        issued_at = datetime.fromtimestamp(jwt_payload["iat"], tz=timezone.utc).replace(tzinfo=None)
        return issued_at < user.tokens_invalidated_at

    # Register blueprints
    from app.routes.auth_route import auth_bp
    from app.routes.driver_route import driver_bp
    from app.routes.ride_route import ride_bp
    from app.routes.admin_route import admin_bp
    from app.routes.payment_route import payment_bp
    from app.routes.kyc_route import kyc_bp
    from app.routes.notification_route import notification_bp
    from app.routes.security_route import security_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(driver_bp)
    app.register_blueprint(ride_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(kyc_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(security_bp)

    # Register socket handlers
    from app.sockets import ride_socket  # noqa: F401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Session no longer valid. Please log in again."}), 401

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app
