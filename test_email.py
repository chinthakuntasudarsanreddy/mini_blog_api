from app.core.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_FROM_EMAIL,
)

from app.utils.email import send_email


print()
print("======================================")
print("       MINI BLOG EMAIL TEST")
print("======================================")

print("SMTP HOST:", SMTP_HOST)
print("SMTP PORT:", SMTP_PORT)
print("SMTP USERNAME:", SMTP_USERNAME)
print("SMTP PASSWORD:", "SET" if SMTP_PASSWORD else "NOT SET")
print("FROM EMAIL:", SMTP_FROM_EMAIL)

print("======================================")
print()


recipient = input(
    "Enter the email address to receive the test email: "
).strip()


if not recipient:
    print("ERROR: Recipient email is required.")
    raise SystemExit(1)


success = send_email(
    recipient=recipient,
    subject="Mini Blog - Test Email",
    body=(
        "Hello!\n\n"
        "This is a test email from the Mini Blogging System.\n\n"
        "If you received this email, your SMTP configuration "
        "is working correctly.\n\n"
        "Thanks,\n"
        "Mini Blogging System"
    )
)


print()
print("======================================")

if success:
    print("TEST RESULT: SUCCESS")
    print("Check the recipient inbox.")
else:
    print("TEST RESULT: FAILED")
    print("Check the error message above.")

print("======================================")