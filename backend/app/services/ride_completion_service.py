from datetime import datetime, timedelta

from app.extensions import db, socketio
from app.models import RideRequest, RideRequestStatus
from app.services.payment.wallet_service import WalletService
from app.services import security_service as sec
from app.utils.geofence import within_radius


def on_driver_location_update(driver):
    """Called whenever a driver's lat/lng changes (REST or socket). Advances
    any of the driver's active rides through the pickup/destination geofence
    states automatically -- no manual "arrived"/"complete" button involved."""
    if driver.current_lat is None or driver.current_lng is None:
        return

    _check_pickup_geofence(driver)
    _check_destination_geofence(driver)


def _check_pickup_geofence(driver):
    accepted = RideRequest.query.filter_by(
        driver_id=driver.id, status=RideRequestStatus.ACCEPTED
    ).all()
    for ride_req in accepted:
        if ride_req.pickup_lat is None or ride_req.pickup_lng is None:
            continue

        if not ride_req.driver_arrived_at and within_radius(
            driver.current_lat, driver.current_lng,
            ride_req.pickup_lat, ride_req.pickup_lng,
            sec.GEOFENCE_ARRIVED_METERS,
        ):
            ride_req.driver_near_pickup = True
            ride_req.driver_arrived_at = datetime.utcnow()
            db.session.commit()
            _emit_and_notify(ride_req, "driver_arrived_at_pickup")
            continue

        if not ride_req.driver_near_pickup and within_radius(
            driver.current_lat, driver.current_lng,
            ride_req.pickup_lat, ride_req.pickup_lng,
            sec.GEOFENCE_NEAR_PICKUP_METERS,
        ):
            ride_req.driver_near_pickup = True
            db.session.commit()
            _emit_and_notify(ride_req, "driver_approaching_pickup")


def _check_destination_geofence(driver):
    ongoing = RideRequest.query.filter_by(
        driver_id=driver.id, status=RideRequestStatus.ONGOING
    ).all()
    for ride_req in ongoing:
        zone = ride_req.zone
        if not zone or zone.lat is None or zone.lng is None:
            continue  # can't geofence-validate a zone with no coordinates configured

        if within_radius(driver.current_lat, driver.current_lng, zone.lat, zone.lng,
                          sec.GEOFENCE_DESTINATION_METERS):
            ride_req.status = RideRequestStatus.AWAITING_COMPLETION
            ride_req.awaiting_completion_at = datetime.utcnow()
            ride_req.completion_deadline = datetime.utcnow() + timedelta(
                minutes=sec.COMPLETION_AUTO_RELEASE_MINUTES
            )
            db.session.commit()
            _emit_and_notify(ride_req, "ride_awaiting_completion")


def _emit_and_notify(ride_req, socket_event):
    socketio.emit(socket_event, ride_req.to_dict(), namespace="/rides",
                   room=f"student_{ride_req.student_id}")
    socketio.emit("ride_request_update", ride_req.to_dict(), namespace="/rides",
                   room=f"student_{ride_req.student_id}")

    from app.services.notification_service import notify
    from app.models import NotificationEvent
    event_map = {
        "driver_approaching_pickup": NotificationEvent.DRIVER_APPROACHING,
        "driver_arrived_at_pickup": NotificationEvent.DRIVER_ARRIVED,
        "ride_awaiting_completion": NotificationEvent.RIDE_AWAITING_CONFIRMATION,
    }
    if socket_event in event_map:
        notify(ride_req.student_id, event_map[socket_event])


def confirm_completion(ride_req):
    """Student confirms the ride happened -- releases held funds immediately."""
    if ride_req.payment_reference:
        WalletService.complete_ride_payment(
            student_id=ride_req.student_id,
            driver_user_id=ride_req.driver.user_id,
            amount=ride_req.price,
            reference=ride_req.payment_reference,
        )
    ride_req.status = RideRequestStatus.COMPLETED
    ride_req.completed_at = datetime.utcnow()
    db.session.commit()

    socketio.emit("ride_request_update", ride_req.to_dict(), namespace="/rides",
                   room=f"driver_{ride_req.driver_id}")

    from app.services.notification_service import notify
    from app.models import NotificationEvent
    notify(ride_req.student_id, NotificationEvent.RIDE_COMPLETED)
    if ride_req.driver and ride_req.driver.user_id:
        notify(ride_req.driver.user_id, NotificationEvent.RIDE_COMPLETED)


def report_problem(ride_req, reason):
    """Student reports an issue instead of confirming -- moves the ride to
    DISPUTED and keeps funds held pending admin review."""
    ride_req.status = RideRequestStatus.DISPUTED
    ride_req.dispute_reason = reason
    ride_req.disputed_at = datetime.utcnow()
    db.session.commit()

    socketio.emit("ride_request_update", ride_req.to_dict(), namespace="/rides",
                   room=f"driver_{ride_req.driver_id}")

    from app.services.notification_service import notify
    from app.models import NotificationEvent
    if ride_req.driver and ride_req.driver.user_id:
        notify(ride_req.driver.user_id, NotificationEvent.DISPUTE_OPENED)


def auto_release_overdue_completions():
    """Rides left in AWAITING_COMPLETION past their completion_deadline with
    no student response are auto-released to the driver. Call periodically
    from a scheduler/cron, or opportunistically from read endpoints."""
    now = datetime.utcnow()
    overdue = RideRequest.query.filter(
        RideRequest.status == RideRequestStatus.AWAITING_COMPLETION,
        RideRequest.completion_deadline.isnot(None),
        RideRequest.completion_deadline < now,
    ).all()
    released = []
    for ride_req in overdue:
        confirm_completion(ride_req)
        released.append(ride_req.id)
    return released
