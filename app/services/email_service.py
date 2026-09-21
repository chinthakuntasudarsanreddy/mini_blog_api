import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from dotenv import load_dotenv

load_dotenv()


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "2525"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

SMTP_FROM_EMAIL = os.getenv(
    "SMTP_FROM_EMAIL",
    "no-reply@blogmanagement.com"
)

SMTP_FROM_NAME = os.getenv(
    "SMTP_FROM_NAME",
    "Blog Management System"
)


def send_email(
    recipient_email: str,
    subject: str,
    body: str
):
    try:
        if not SMTP_HOST:
            raise ValueError("SMTP_HOST is not configured")

        if not SMTP_USERNAME:
            raise ValueError("SMTP_USERNAME is not configured")

        if not SMTP_PASSWORD:
            raise ValueError("SMTP_PASSWORD is not configured")

        message = EmailMessage()

        message["From"] = formataddr(
            (SMTP_FROM_NAME, SMTP_FROM_EMAIL)
        )

        message["To"] = recipient_email
        message["Subject"] = subject

        message.set_content(body)

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
            timeout=20
        ) as smtp:

            smtp.starttls()

            smtp.login(
                SMTP_USERNAME,
                SMTP_PASSWORD
            )

            smtp.send_message(message)

        print(
            f"Email sent successfully to {recipient_email}"
        )

    except Exception as exc:
        print(
            f"Email sending failed for "
            f"{recipient_email}: {exc}"
        )