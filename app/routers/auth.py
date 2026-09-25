from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    # Check username
    existing_username = (
        db.query(User)
        .filter(User.username == user_data.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Check email
    existing_email = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create local user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        provider="local",
        provider_id=None,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == login_data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Social/Auth0 users don't have a local password
    if not user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                "This account uses social login. "
                "Please continue with Google or Facebook."
            ),
        )

    if not verify_password(
        login_data.password,
        user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }