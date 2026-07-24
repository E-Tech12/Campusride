# import os
# import smtplib
# from dotenv import load_dotenv

# load_dotenv()

# email = os.getenv("SMTP_USERNAME")
# password = os.getenv("SMTP_PASSWORD")

# print("EMAIL:", email)
# print("PASSWORD EXISTS:", bool(password))

# try:
#     server = smtplib.SMTP("smtp.gmail.com", 587)
#     server.starttls()
#     server.login(email, password)

#     print("\n✅ SMTP LOGIN SUCCESS")
#     server.quit()

# except Exception as e:
#     print("\n❌ SMTP LOGIN FAILED")
#     print(e)
    
    
    
    
#     import os
# from dotenv import load_dotenv

# load_dotenv()

# print("=" * 50)
# print("SMTP_USERNAME:", os.getenv("SMTP_USERNAME"))
# print("SMTP_PASSWORD:", os.getenv("SMTP_PASSWORD"))
# print("SMTP_HOST:", os.getenv("SMTP_HOST"))
# print("SMTP_PORT:", os.getenv("SMTP_PORT"))
# print("RESEND_API_KEY:", os.getenv("RESEND_API_KEY"))
# print("=" * 50)

# import smtplib
# from email.mime.text import MIMEText

# SMTP_USERNAME = "cyberdev203@gmail.com"
# SMTP_PASSWORD = "ctkmmvmpbjfhrwek"

# FROM = SMTP_USERNAME
# TO = "adediraneric592@gmail.com"  # email you want to receive the test mail

# msg = MIMEText("This is a test email from SMTP.")
# msg["Subject"] = "SMTP Test"
# msg["From"] = FROM
# msg["To"] = TO

# try:
#     server = smtplib.SMTP("smtp.gmail.com", 587)
#     server.starttls()

#     server.login(
#         SMTP_USERNAME,
#         SMTP_PASSWORD
#     )

#     server.sendmail(
#         FROM,
#         TO,
#         msg.as_string()
#     )

#     server.quit()

#     print("✅ Email sent successfully")

# except Exception as e:
#     print("❌ SMTP failed:")
#     print(e)