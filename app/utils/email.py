import smtplib
from email.message import EmailMessage
from typing import Optional

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
    body: str,
) -> bool:
    """
    Send an email through the configured SMTP server.

    Returns:
        True  -> Email sent successfully
        False -> Email sending failed
    """

    try:
        # Validate SMTP configuration
        if not SMTP_HOST:
            print("EMAIL ERROR: SMTP_HOST is missing")
            return False

        if not SMTP_PORT:
            print("EMAIL ERROR: SMTP_PORT is missing")
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

        if not recipient:
            print("EMAIL ERROR: Recipient email is missing")
            return False

        # Create email message
        message = EmailMessage()
        message["From"] = SMTP_FROM_EMAIL
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        # Debug information
        print("========== EMAIL DEBUG ==========")
        print("SMTP HOST:", SMTP_HOST)
        print("SMTP PORT:", SMTP_PORT)
        print("SMTP USERNAME:", SMTP_USERNAME)
        print("SMTP PASSWORD: ******")
        print("FROM EMAIL:", SMTP_FROM_EMAIL)
        print("TO EMAIL:", recipient)
        print("SUBJECT:", subject)
        print("=================================")

        # Connect to SMTP server
        with smtplib.SMTP(
            host=SMTP_HOST,
            port=int(SMTP_PORT),
            timeout=30,
        ) as server:

            server.ehlo()
            print("SMTP connection successful")

            # Start TLS encryption
            server.starttls()
            server.ehlo()
            print("TLS connection successful")

            # Login to SMTP server
            server.login(
                SMTP_USERNAME,
                SMTP_PASSWORD,
            )
            print("SMTP login successful")

            # Send email
            server.send_message(message)

            print(f"EMAIL SENT SUCCESSFULLY TO: {recipient}")

        return True

    except smtplib.SMTPAuthenticationError as error:
        print("EMAIL ERROR: SMTP authentication failed")
        print("Check your SMTP username and password.")
        print("DETAIL:", error)
        return False

    except smtplib.SMTPConnectError as error:
        print("EMAIL ERROR: Could not connect to SMTP server")
        print("DETAIL:", error)
        return False

    except smtplib.SMTPServerDisconnected as error:
        print("EMAIL ERROR: SMTP server disconnected")
        print("DETAIL:", error)
        return False

    except smtplib.SMTPException as error:
        print("EMAIL ERROR: SMTP error")
        print("DETAIL:", error)
        return False

    except ValueError as error:
        print("EMAIL ERROR: Invalid SMTP port or configuration")
        print("DETAIL:", error)
        return False

    except Exception as error:
        print("EMAIL ERROR:", type(error).__name__)
        print("DETAIL:", error)
        return False