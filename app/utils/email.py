import smtplib
from email.message import EmailMessage

from app.core.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_FROM_EMAIL,
)


def send_email(
    recipient: str,
    subject: str,
    body: str
) -> bool:

    try:
        if not SMTP_HOST:
            print("EMAIL ERROR: SMTP_HOST is missing")
            return False

        if not SMTP_USERNAME:
            print("EMAIL ERROR: SMTP_USERNAME is missing")
            return False

        if not SMTP_PASSWORD:
            print("EMAIL ERROR: SMTP_PASSWORD is missing")
            return False

        if not SMTP_FROM_EMAIL:
            print("EMAIL ERROR: SMTP_FROM_EMAIL is missing")
            return False

        message = EmailMessage()

        message["From"] = SMTP_FROM_EMAIL
        message["To"] = recipient
        message["Subject"] = subject

        message.set_content(body)

        print("========== EMAIL DEBUG ==========")
        print("SMTP HOST:", SMTP_HOST)
        print("SMTP PORT:", SMTP_PORT)
        print("SMTP USERNAME:", SMTP_USERNAME)
        print("FROM EMAIL:", SMTP_FROM_EMAIL)
        print("TO EMAIL:", recipient)
        print("SUBJECT:", subject)
        print("=================================")

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
            timeout=30
        ) as server:

            server.ehlo()

            print("SMTP connection successful")

            server.starttls()

            print("TLS connection successful")

            server.ehlo()

            server.login(
                SMTP_USERNAME,
                SMTP_PASSWORD
            )

            print("SMTP login successful")

            server.send_message(message)

            print(
                f"EMAIL SENT SUCCESSFULLY TO: {recipient}"
            )

        return True

    except smtplib.SMTPAuthenticationError as e:
        print("EMAIL ERROR: SMTP authentication failed")
        print("Check SMTP_USERNAME and SMTP_PASSWORD")
        print("DETAIL:", e)
        return False

    except smtplib.SMTPConnectError as e:
        print("EMAIL ERROR: Could not connect to SMTP server")
        print("DETAIL:", e)
        return False

    except smtplib.SMTPException as e:
        print("EMAIL ERROR: SMTP error")
        print("DETAIL:", e)
        return False

    except Exception as e:
        print("EMAIL ERROR:", type(e).__name__)
        print("DETAIL:", e)
        return False