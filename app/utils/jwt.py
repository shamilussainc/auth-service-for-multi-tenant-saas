from enum import Enum
from datetime import datetime, timedelta, timezone
import jwt
from app.settings import settings
from app.schemas import TokenType, TokenData


def create_token(data: dict, token_type: TokenType, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        if token_type == TokenType.ACCESS:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=1)

    to_encode.update({"exp": expire, "token_type": token_type.name})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY.get_secret_value(
    ), algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    return create_token(data=data, token_type=TokenType.ACCESS, expires_delta=expires_delta)


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    return create_token(data=data, token_type=TokenType.REFRESH, expires_delta=expires_delta)


def decode_token(token: str) -> TokenData:
    payload = jwt.decode(token, settings.JWT_SECRET_KEY.get_secret_value(
    ), algorithms=[settings.JWT_ALGORITHM])

    return TokenData(email=payload.get("sub"), token_type=TokenType[payload.get("token_type")])
