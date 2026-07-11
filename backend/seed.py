"""
Run this once after migrations to create an initial admin user and a few sample zones.
Usage: python seed.py
"""
from app import create_app
from app.extensions import db
from app.models import User, UserRole, Zone

app = create_app()

with app.app_context():
    # --- Admin user ---
    admin_email = "admin@campusride.ng"
    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            email="admin@campusride.ng",
            username="admin",
            full_name="System Admin",
            student_id="ADMIN-0001",
            role=UserRole.ADMIN,
            is_verified=True,
        )
        admin.set_password("Admin1234")
        db.session.add(admin)
        print(f"Created admin user: {admin_email} / Admin1234 (change this password)")
    else:
        print("Admin user already exists, skipping.")

    # --- Sample zones ---
    sample_zones = [
        ("Gate", 200.0),
        ("Colerm", 250.0),
        ("Colerm Phase 2", 250.0),
        ("Mancot", 150.0),
        ("Jao3", 250.0),
        ("Mahmoud", 250.0),
        ("1k Cap", 250.0),
        ("Colanim", 250.0),
        ("Coplant", 250.0),
    ]
    for name, price in sample_zones:
        if not Zone.query.filter_by(name=name).first():
            db.session.add(Zone(name=name, price=price))
            print(f"Created zone: {name} (₦{price})")

    db.session.commit()
    print("Seeding complete.")