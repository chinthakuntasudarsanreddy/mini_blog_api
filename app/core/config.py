import os

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# SMTP CONFIGURATION
# ============================================================

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")


def validate_smtp_config():
    required = {
        "SMTP_HOST": SMTP_HOST,
        "SMTP_USERNAME": SMTP_USERNAME,
        "SMTP_PASSWORD": SMTP_PASSWORD,
        "SMTP_FROM_EMAIL": SMTP_FROM_EMAIL,
    }

    missing = [
        name
        for name, value in required.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Missing SMTP environment variables: "
            + ", ".join(missing)
        )


# ============================================================
# AUTH0 CONFIGURATION
# ============================================================

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
AUTH0_ALGORITHMS = os.getenv("AUTH0_ALGORITHMS", "RS256")


def validate_auth0_config():
    required = {
        "AUTH0_DOMAIN": AUTH0_DOMAIN,
        "AUTH0_AUDIENCE": AUTH0_AUDIENCE,
    }

    missing = [
        name
        for name, value in required.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Missing Auth0 environment variables: "
            + ", ".join(missing)
        )