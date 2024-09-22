from typing import Annotated
import jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from fastapi.security import OAuth2PasswordBearer
from app.database import SessionLocal
from app.utils.jwt import decode_token
from app.models import User as UserModel
from app import crud


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/sign_in")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db .close()


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = decode_token(token)
        if token_data.email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = crud.get_user_by_email(db=db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    if current_user.status == 0:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
