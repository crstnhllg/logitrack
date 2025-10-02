from app.schemas.user import (
    UserResponse,
    UpdateUserRequest,
    UpdateRoleRequest,
    PasswordRequest,
)
from app.schemas.common import MessageResponse
from app.core.security import bcrypt_context
from app.dependencies import user_dependency
from app.database import db_dependency
from starlette import status
from app.models import User
from fastapi import APIRouter, HTTPException, Path


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_me(user: user_dependency):
    """Retrieve details of the currently authenticated user."""
    return user


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[UserResponse])
def get_all_users(db: db_dependency, user: user_dependency):
    """Retrieve a list of all users."""
    return db.query(User).all()


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_user_by_id(db: db_dependency, user: user_dependency, user_id: int = Path(gt=0)):
    """Retrieve a user by their unique ID."""
    requested_user = db.get(User, user_id)
    if requested_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specified user could not be found.",
        )

    return requested_user


@router.put("/password", status_code=status.HTTP_200_OK, response_model=MessageResponse)
def update_user_password(
    db: db_dependency, user: user_dependency, update_request: UpdateUserRequest
):
    """Update the password of the currently authenticated user."""
    if not bcrypt_context.verify(update_request.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The old password you entered is incorrect.",
        )

    user.hashed_password = bcrypt_context.hash(update_request.new_password)
    db.commit()

    return MessageResponse(
        status="success", message="Password has been updated successfully."
    )


@router.put(
    "/{user_id}/role", status_code=status.HTTP_200_OK, response_model=UserResponse
)
def update_user_role(
    db: db_dependency,
    user: user_dependency,
    update_request: UpdateRoleRequest,
    user_id: int = Path(gt=0),
):
    """Update the role of a user by their ID (admin only)."""
    target_user = db.get(User, user_id)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specified user could not be found.",
        )
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this action.",
        )

    target_user.role = update_request.role
    db.commit()
    db.refresh(target_user)

    return target_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    db: db_dependency, user: user_dependency, password_request: PasswordRequest
):
    """Delete the account of the currently authenticated user."""
    me = db.get(User, user.id)

    if not bcrypt_context.verify(password_request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The password you entered is incorrect.",
        )

    db.delete(me)
    db.commit()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(
    db: db_dependency, user: user_dependency, user_id: int = Path(gt=0)
):
    """Delete a user by their ID (admin only)."""
    target_user = db.get(User, user_id)

    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specified user could not be found.",
        )
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this action.",
        )

    db.delete(target_user)
    db.commit()
