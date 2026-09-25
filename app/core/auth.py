from functools import lru_cache
import ssl

import certifi
import jwt
from jwt import PyJWKClient

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import AUTH0_DOMAIN, AUTH0_AUDIENCE
from app.core.database import get_db
from app.models.user import User


security = HTTPBearer()


@lru_cache()
def get_jwks_client():
    """
    Create Auth0 JWKS client using certifi's
    trusted CA certificate bundle.
    """

    ssl_context = ssl.create_default_context(
        cafile=certifi.where()
    )

    return PyJWKClient(
        f"https://{AUTH0_DOMAIN}/.well-known/jwks.json",
        ssl_context=ssl_context,
    )


def verify_auth0_token(token: str) -> dict:
    """
    Verify an Auth0 RS256 access token.
    """

    if not AUTH0_DOMAIN:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AUTH0_DOMAIN is missing",
        )

    if not AUTH0_AUDIENCE:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AUTH0_AUDIENCE is missing",
        )

    try:
        jwks_client = get_jwks_client()

        signing_key = jwks_client.get_signing_key_from_jwt(
            token
        )

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=AUTH0_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )

        print("AUTH0 TOKEN VALID")
        print("AUTH0 SUB:", payload.get("sub"))
        print("AUTH0 AUDIENCE:", payload.get("aud"))
        print("AUTH0 ISSUER:", payload.get("iss"))

        return payload

    except jwt.ExpiredSignatureError:
        print("AUTH0 ERROR: Token expired")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth0 token has expired",
        )

    except jwt.InvalidAudienceError:
        print("AUTH0 ERROR: Invalid audience")
        print("Expected:", AUTH0_AUDIENCE)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth0 audience",
        )

    except jwt.InvalidIssuerError:
        print("AUTH0 ERROR: Invalid issuer")
        print(
            "Expected:",
            f"https://{AUTH0_DOMAIN}/",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth0 issuer",
        )

    except jwt.InvalidSignatureError:
        print("AUTH0 ERROR: Invalid signature")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth0 signature",
        )

    except jwt.PyJWTError as exc:
        print(
            "AUTH0 ERROR:",
            type(exc).__name__,
            str(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Auth0 token",
        )

    except Exception as exc:
        print(
            "AUTH0 ERROR:",
            type(exc).__name__,
            str(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to validate Auth0 token",
        )


def get_current_auth0_payload(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
):
    """
    Get decoded Auth0 JWT payload.
    """

    token = credentials.credentials

    return verify_auth0_token(token)


def get_current_user(
    payload: dict = Depends(get_current_auth0_payload),
    db: Session = Depends(get_db),
):
    """
    Find or create the local database user
    associated with the Auth0 account.
    """

    auth0_user_id = payload.get("sub")

    if not auth0_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth0 token does not contain a user identifier",
        )

    email = payload.get("email")

    name = (
        payload.get("name")
        or payload.get("nickname")
        or payload.get("preferred_username")
    )

    if "|" in auth0_user_id:
        provider = auth0_user_id.split("|", 1)[0]
    else:
        provider = "auth0"

    # Find existing Auth0 user
    user = (
        db.query(User)
        .filter(User.provider_id == auth0_user_id)
        .first()
    )

    if user:
        changed = False

        if email and user.email != email:
            user.email = email
            changed = True

        if name and user.username != name[:50]:
            user.username = name[:50]
            changed = True

        if user.provider != provider:
            user.provider = provider
            changed = True

        if changed:
            db.commit()
            db.refresh(user)

        return user

    # Try matching existing user by email
    if email:
        existing_email_user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing_email_user:
            existing_email_user.provider = provider
            existing_email_user.provider_id = auth0_user_id

            if name:
                existing_email_user.username = name[:50]

            db.commit()
            db.refresh(existing_email_user)

            return existing_email_user

    # Create new Auth0 user
    if email:
        username = (
            name or email.split("@")[0]
        )[:50]

        original_username = username
        counter = 1

        while (
            db.query(User)
            .filter(User.username == username)
            .first()
        ):
            suffix = str(counter)

            username = (
                original_username[:50 - len(suffix)]
                + suffix
            )

            counter += 1

        new_user = User(
            username=username,
            email=email,
            password=None,
            provider=provider,
            provider_id=auth0_user_id,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email is missing from Auth0 token",
    )