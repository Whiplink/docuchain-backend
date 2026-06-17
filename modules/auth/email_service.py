import os
import smtplib
from email.message import EmailMessage


class EmailService:
    def send_otp(self, email: str, otp: str):
        msg = EmailMessage()
        msg["Subject"] = "Your OTP Code"
        msg["From"] = os.getenv("MAIL_USERNAME")
        msg["To"] = email

        msg.set_content(
            f"Your verification code is: {otp}\n\nExpires in 5 minutes."
        )

        with smtplib.SMTP(
            os.getenv("MAIL_SERVER"),
            int(os.getenv("MAIL_PORT"))
        ) as smtp:
            smtp.starttls()
            smtp.login(
                os.getenv("MAIL_USERNAME"),
                os.getenv("MAIL_PASSWORD")
            )
            smtp.send_message(msg)