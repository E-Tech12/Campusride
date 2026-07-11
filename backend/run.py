from app import create_app
from app.extensions import socketio, db, migrate

app = create_app()


def run_pending_migrations():
    """Apply any pending Alembic migrations automatically on startup.
    This keeps local/dev environments in sync without a manual step, while
    `apply_migrations.py` remains available for CI/production deploys where
    running migrations as an explicit, separate step is preferred."""
    from flask_migrate import upgrade
    try:
        with app.app_context():
            upgrade()
        print("[migrations] database is up to date.")
    except Exception as e:
        print(f"[migrations] skipped auto-migration ({e}). "
              f"Run `python apply_migrations.py` manually if needed.")


if __name__ == "__main__":
    run_pending_migrations()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
