from flask_socketio import join_room, leave_room, emit
from flask_jwt_extended import decode_token

from app.extensions import socketio, db
from app.models import User, Driver


def _user_from_token(token):
    try:
        decoded = decode_token(token)
        user_id = int(decoded["sub"])
        return User.query.get(user_id)
    except Exception:
        return None


@socketio.on("connect", namespace="/rides")
def handle_connect(auth):
    token = (auth or {}).get("token") if isinstance(auth, dict) else None
    user = _user_from_token(token) if token else None
    if not user:
        return False  # reject connection
    # Join personal room so server can target events at this user
    join_room(f"student_{user.id}")
    if user.driver_profile:
        join_room(f"driver_{user.driver_profile.id}")
    emit("connected", {"message": "connected", "user_id": user.id})


@socketio.on("disconnect", namespace="/rides")
def handle_disconnect():
    pass

@socketio.on("subscribe_location", namespace="/rides")
def handle_subscribe_location(data=None):
    join_room("location_updates")

@socketio.on("unsubscribe_location", namespace="/rides")
def handle_unsubscribe_location(data=None):
    leave_room("location_updates")


@socketio.on("driver_location_ping", namespace="/rides")
def handle_driver_location_ping(data):
    """Lightweight live-location broadcast from a driver's client over the socket
    (in addition to the REST /api/driver/location fallback)."""
    driver_id = data.get("driver_id")
    lat = data.get("lat")
    lng = data.get("lng")
    if driver_id is None or lat is None or lng is None:
        return

    driver = Driver.query.get(driver_id)
    if not driver:
        return

    driver.current_lat = lat
    driver.current_lng = lng
    db.session.commit()

    emit("driver_location_update", {
        "driver_id": driver_id, "lat": lat, "lng": lng
    }, namespace="/rides", room="location_updates")

    from app.services import ride_completion_service
    ride_completion_service.on_driver_location_update(driver)
