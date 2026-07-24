import os
import json
import threading

from app.extensions import db
from app.models import DeviceToken, NotificationLog, NotificationEvent

_firebase_app = None
_firebase_lock = threading.Lock()


def _get_firebase_app():
    """Lazily initializes the Firebase Admin SDK from a service-account JSON
    given either as a file path (FIREBASE_CREDENTIALS_PATH) or as an inline
    JSON blob (FIREBASE_CREDENTIALS_JSON) -- whichever env var is set."""
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    with _firebase_lock:
        if _firebase_app is not None:
            return _firebase_app
        try:
            import firebase_admin
            from firebase_admin import credentials
        except ImportError:
            return None

        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

        try:
            if cred_json:
                cred = credentials.Certificate(json.loads(cred_json))
            elif cred_path:
                cred = credentials.Certificate(cred_path)
            else:
                return None
            _firebase_app = firebase_admin.initialize_app(cred)
        except Exception:
            return None
        return _firebase_app


NOTIFICATION_COPY = {
    NotificationEvent.RIDE_ACCEPTED: ("Ride accepted", "Your driver accepted your ride request."),
    NotificationEvent.DRIVER_APPROACHING: ("Driver approaching", "Your driver is almost at your pickup point."),
    NotificationEvent.DRIVER_ARRIVED: ("Driver arrived", "Your driver has arrived at your pickup point."),
    NotificationEvent.RIDE_STARTED: ("Ride started", "Your ride is now in progress."),
    NotificationEvent.RIDE_AWAITING_CONFIRMATION: ("Confirm your ride", "Your driver has reached your destination. Please confirm."),
    NotificationEvent.RIDE_COMPLETED: ("Ride completed", "Your ride has been completed. Thanks for riding with CampusRide!"),
    NotificationEvent.DISPUTE_OPENED: ("Dispute opened", "A dispute has been opened on a recent ride."),
    NotificationEvent.DEPOSIT_SUCCESSFUL: ("Deposit successful", "Your wallet deposit was successful."),
    NotificationEvent.WITHDRAWAL_APPROVED: ("Withdrawal approved", "Your withdrawal has been approved and is on its way."),
    NotificationEvent.WITHDRAWAL_FAILED: ("Withdrawal failed", "Your withdrawal request could not be processed."),
    NotificationEvent.PASSWORD_CHANGED: ("Password changed", "Your password was just changed. If this wasn't you, contact support immediately."),
    NotificationEvent.SUSPICIOUS_LOGIN: ("New login detected", "We noticed a login from a new device or location."),
    NotificationEvent.KYC_APPROVED: ("Verification approved", "Your driver identity verification has been approved."),
    NotificationEvent.KYC_REJECTED: ("Verification rejected", "Your driver identity verification was rejected. Please review and resubmit."),
}


def notify(user_id, event: NotificationEvent, data=None, title=None, body=None):
    """Sends a push notification to every active device token for a user and
    records it in NotificationLog regardless of delivery outcome. Safe to call
    even when Firebase isn't configured -- it will just log un-delivered."""
    default_title, default_body = NOTIFICATION_COPY.get(event, (event.value.replace("_", " ").title(), ""))
    title = title or default_title
    body = body or default_body

    log = NotificationLog(
        user_id=user_id, event=event, title=title, body=body, data=data or {},
        delivered=False,
    )
    db.session.add(log)
    db.session.commit()

    app = _get_firebase_app()
    tokens = DeviceToken.query.filter_by(user_id=user_id, is_active=True).all()
    if not app or not tokens:
        if not app:
            log.error = "FCM not configured (set FIREBASE_CREDENTIALS_PATH or FIREBASE_CREDENTIALS_JSON)"
        db.session.commit()
        return log

    from firebase_admin import messaging

    delivered_any = False
    for device in tokens:
        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in (data or {}).items()},
                token=device.token,
            )
            messaging.send(message)
            delivered_any = True
        except Exception as e:
            err_str = str(e)
            # Prune tokens Firebase says are no longer valid.
            if "registration-token-not-registered" in err_str.lower() or "invalid-argument" in err_str.lower():
                device.is_active = False
            log.error = err_str[:500]

    log.delivered = delivered_any
    db.session.commit()
    return log
