import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")


def send_otp_email(email, otp_code, purpose="email_verification"):
    if purpose == "password_reset":
        subject = "CampusRide Password Reset Code"
        heading = "Password Reset Request"
    else:
        subject = "CampusRide Email Verification"
        heading = "Verify Your Email"

    resend.Emails.send({
        "from": "CampusRide <onboarding@resend.dev>",
        "to": [email],
        "subject": subject,
        "html": f"""
        <div style="font-family:Arial,sans-serif;padding:20px">
            <h2>{heading}</h2>
            <p>Your verification code is:</p>

            <div style="
                font-size:32px;
                font-weight:bold;
                letter-spacing:5px;
                padding:15px;
                background:#f5f5f5;
                display:inline-block;
                border-radius:8px;
            ">
                {otp_code}
            </div>

            <p style="margin-top:20px;">
                This code expires in 10 minutes.
            </p>

            <p>
                If you did not request this, please ignore this email.
            </p>
        </div>
        """
    })