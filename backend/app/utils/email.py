import os
import smtplib
import resend

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart






# Resend API key
resend.api_key = os.getenv("RESEND_API_KEY")


SMTP_HOST = os.getenv(
    "MAIL_SERVER",
    "smtp.gmail.com"
)

SMTP_PORT = int(
    os.getenv(
        "MAIL_PORT",
        587
    )
)


_PURPOSE_COPY = {
    "email_verification": (
        "CampusRide Email Verification",
        "Verify Your Email"
    ),
    "password_reset": (
        "CampusRide Password Reset Code",
        "Password Reset Request"
    ),
    "password_change": (
        "CampusRide Security Code",
        "Confirm Password Change"
    ),
    "email_change": (
        "CampusRide Security Code",
        "Confirm Email Change"
    ),
    "phone_change": (
        "CampusRide Security Code",
        "Confirm Phone Number Change"
    ),
    "bank_change": (
        "CampusRide Security Code",
        "Confirm Bank Account Change"
    ),
    "withdrawal": (
        "CampusRide Security Code",
        "Confirm Withdrawal"
    ),
    "login_verify": (
        "CampusRide Login Verification",
        "Confirm This Login"
    ),
}


def get_smtp_config():

    return {
        "username": os.getenv(
            "MAIL_USERNAME"
        ),

        "password": os.getenv(
            "MAIL_PASSWORD"
        ),

        "sender": os.getenv(
            "MAIL_DEFAULT_SENDER",
            os.getenv(
                "MAIL_USERNAME"
            )
        )
    }



def build_email_html(
    heading,
    otp_code
):
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{heading}</title>
    </head>

    <body style="
        margin:0;
        padding:0;
        background:#f4f7fb;
        font-family:Arial, Helvetica, sans-serif;
    ">

        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td align="center" style="padding:40px 20px;">

                    <table width="500"
                        cellpadding="0"
                        cellspacing="0"
                        style="
                            background:#ffffff;
                            border-radius:12px;
                            padding:40px;
                            box-shadow:0 4px 15px rgba(0,0,0,0.08);
                        ">

                        <!-- Header -->
                        <tr>
                            <td align="center">

                                <h1 style="
                                    margin:0;
                                    color:#2563eb;
                                    font-size:28px;
                                    font-weight:700;
                                ">
                                    CampusRide
                                </h1>

                                <p style="
                                    color:#64748b;
                                    font-size:14px;
                                    margin-top:8px;
                                ">
                                    Secure account verification
                                </p>

                            </td>
                        </tr>


                        <!-- Message -->

                        <tr>
                            <td style="padding-top:35px;">

                                <h2 style="
                                    color:#111827;
                                    font-size:22px;
                                    margin-bottom:15px;
                                ">
                                    {heading}
                                </h2>


                                <p style="
                                    color:#475569;
                                    font-size:15px;
                                    line-height:1.6;
                                ">
                                    We received a request to verify your
                                    CampusRide account. Use the verification
                                    code below to continue.
                                </p>


                            </td>
                        </tr>


                        <!-- OTP Box -->

                        <tr>
                            <td align="center" style="padding:30px 0;">

                                <div style="
                                    background:#eff6ff;
                                    border:1px solid #bfdbfe;
                                    border-radius:10px;
                                    padding:20px 35px;
                                    display:inline-block;
                                ">

                                    <span style="
                                        font-size:36px;
                                        font-weight:700;
                                        letter-spacing:8px;
                                        color:#1d4ed8;
                                    ">
                                        {otp_code}
                                    </span>

                                </div>

                            </td>
                        </tr>



                        <tr>
                            <td>

                                <p style="
                                    color:#475569;
                                    font-size:14px;
                                    line-height:1.6;
                                ">
                                    This verification code will expire in
                                    <strong>10 minutes</strong>.
                                    For your security, do not share this code
                                    with anyone.
                                </p>


                                <p style="
                                    color:#475569;
                                    font-size:14px;
                                    line-height:1.6;
                                ">
                                    If you did not request this verification,
                                    you can safely ignore this email.
                                </p>

                            </td>
                        </tr>



                        <!-- Footer -->

                        <tr>
                            <td align="center"
                                style="
                                    padding-top:35px;
                                    border-top:1px solid #e5e7eb;
                                ">

                                <p style="
                                    color:#94a3b8;
                                    font-size:12px;
                                    margin:0;
                                ">
                                    © 2026 CampusRide. All rights reserved.
                                </p>

                                <p style="
                                    color:#94a3b8;
                                    font-size:12px;
                                    margin-top:5px;
                                ">
                                    This is an automated security email.
                                    Please do not reply.
                                </p>

                            </td>
                        </tr>


                    </table>

                </td>
            </tr>
        </table>

    </body>
    </html>
    """



def send_via_resend(
    email,
    subject,
    html
):

    resend.Emails.send({

        "from": os.getenv(
            "FROM_EMAIL",
            "CampusRide <onboarding@resend.dev>"
        ),

        "to": [
            email
        ],

        "subject": subject,

        "html": html

    })
    
    



def send_via_smtp(
    email,
    subject,
    html
):

    config = get_smtp_config()


    if not config["username"] or not config["password"]:

        raise Exception(
            "SMTP credentials missing"
        )


    print(
        "[SMTP] USER:",
        config["username"]
    )

    print(
        "[SMTP] PASSWORD LENGTH:",
        len(config["password"])
    )


    msg = MIMEMultipart()

    msg["From"] = config["sender"]

    msg["To"] = email

    msg["Subject"] = subject


    msg.attach(
        MIMEText(
            html,
            "html"
        )
    )


    server = smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT
    )


    server.starttls()


    server.login(
        config["username"],
        config["password"]
    )


    server.send_message(
        msg
    )


    server.quit()




def send_otp_email(
    email,
    otp_code,
    purpose="email_verification"
):


    subject, heading = _PURPOSE_COPY.get(
        purpose,

        (
            "CampusRide Verification Code",
            "Verify This Action"
        )
    )


    html = build_email_html(
        heading,
        otp_code
    )



    # Try Resend first

    try:

        send_via_resend(
            email,
            subject,
            html
        )


        print(
            f"[EMAIL] Sent through Resend -> {email}"
        )


        return True


    except Exception as resend_error:


        print(
            f"[EMAIL] Resend failed: {resend_error}"
        )



    # Fallback to Gmail SMTP

    try:

        send_via_smtp(
            email,
            subject,
            html
        )


        print(
            f"[EMAIL] Sent through SMTP -> {email}"
        )


        return True


    except Exception as smtp_error:


        print(
            f"[EMAIL] SMTP failed: {smtp_error}"
        )


        return False