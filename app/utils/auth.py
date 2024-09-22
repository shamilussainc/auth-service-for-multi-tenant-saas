from app.crud import get_user_by_email
from sqlalchemy.orm import Session
from app.utils.hashing import verify_password


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db=db, email=email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user
