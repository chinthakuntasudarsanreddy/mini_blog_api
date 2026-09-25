from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_auth0_payload
from app.core.database import get_db
from app.models.user import User


def get_current_auth0_user(
    payload: dict = Depends(get_current_auth0_payload),
    db: Session = Depends(get_db),
):
    """
    Get the local database user associated with
    the authenticated Auth0 account.
    """

    auth0_user_id = payload.get("sub")

    if not auth0_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth0 user ID is missing",
        )

    # Access tokens may not contain email/name.
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

    # -------------------------------------------------
    # 1. Find user using Auth0 provider_id
    # -------------------------------------------------

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

    # -------------------------------------------------
    # 2. If email exists, try matching existing user
    # -------------------------------------------------

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

    # -------------------------------------------------
    # 3. Create new Auth0 user
    # -------------------------------------------------

    # If Auth0 access token doesn't contain email,
    # create a safe fallback email identifier.
    if not email:
        email = f"{auth0_user_id}@auth0.local"

    username = (
        name
        or email.split("@")[0]
        or "auth0user"
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