"""
Standalone migration runner.

Use this in production/CI deploys where you want migrations applied as an
explicit step (e.g. in a release hook) rather than automatically on server
boot. `run.py` also auto-applies pending migrations on local/dev startup, so
this script is the second half of the dual migration strategy.

Usage: python apply_migrations.py
"""
from app import create_app
from flask_migrate import upgrade

app = create_app()

with app.app_context():
    upgrade()
    print("Migrations applied successfully.")
