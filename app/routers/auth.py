from app.core.security import bcrypt_context, create_access_token
from app.schemas.user import CreateUserRequest, UserResponse
from app.models import User
from app.database import db_dependency
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from datetime import timedelta
from starlette import status
from sqlalchemy import or_


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(db: db_dependency, create_user_request: CreateUserRequest) -> User:
    """Create a new user account with a unique username and email."""
    user_exists = (
        db.query(User)
        .filter(
            or_(
                User.username == create_user_request.username,
                User.email == create_user_request.email,
            )
        )
        .first()
    )

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this username or email already exists.",
        )

    requested_data = create_user_request.model_dump(exclude={"password"})
    hashed_password = bcrypt_context.hash(create_user_request.password)
    new_user = User(**requested_data, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/token", status_code=status.HTTP_200_OK)
def login_for_access_token(
    db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> dict:
    """Authenticate a user and return a JWT access token for authorization."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if user is None or not bcrypt_context.verify(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password. Please check your credentials and try again.",
        )

    token = create_access_token(user.username, user.id, timedelta(minutes=60))

    return {
        "access_token": token,
        "token_type": "bearer",
    }
