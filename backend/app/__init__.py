import os
from flask import Flask, app, jsonify
from dotenv import load_dotenv

from app.extensions import db, migrate, jwt, cors, mail, socketio, limiter

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")

    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True") == "True"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173,https://campusride-bolt.vercel.app/")

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": frontend_url}}, supports_credentials=True)
    socketio.init_app(app, cors_allowed_origins=frontend_url)

    # Import models so Alembic can see them
    from app import models  # noqa: F401

    # Register blueprints
    from app.routes.auth_route import auth_bp
    from app.routes.driver_route import driver_bp
    from app.routes.ride_route import ride_bp
    from app.routes.admin_route import admin_bp
    from app.routes.payment_route import payment_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(driver_bp)
    app.register_blueprint(ride_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payment_bp)

    # Register socket handlers
    from app.sockets import ride_socket  # noqa: F401

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
