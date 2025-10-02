from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.models import User
from app.database import db_dependency
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from typing import Annotated
from starlette import status
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_access_token(username: str, user_id: int, expiry_time: timedelta) -> str:
    expires = datetime.now(timezone.utc) + expiry_time
    encode = {
        "sub": username,
        "id": user_id,
        "exp": expires,
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    db: db_dependency, token: Annotated[str, Depends(oauth2_bearer)]
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )
    current_user = db.get(User, payload.get("id"))
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )
    return current_user
