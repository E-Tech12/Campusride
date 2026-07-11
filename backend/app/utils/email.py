from flask_mail import Message
from app.extensions import mail


def send_otp_email(to_email, otp_code, purpose="email_verification"):
    subject_map = {
        "email_verification": "Verify your CampusRide account",
        "password_reset": "Reset your CampusRide password",
        "login": "Your CampusRide login code",
    }
    subject = subject_map.get(purpose, "Your CampusRide verification code")

    body = f"""Hi,

Your CampusRide verification code is: {otp_code}

This code expires in 10 minutes. If you didn't request this, you can ignore this email.

- CampusRide Team
"""
    msg = Message(subject=subject, recipients=[to_email], body=body)
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"[mail error] failed to send OTP email: {e}")
        return False
