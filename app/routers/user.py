from datetime import timedelta
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, Form, BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import get_current_active_user, get_db
from app import crud, schemas
from app.models import User as UserModel
from app.utils.auth import authenticate_user
from app.utils.jwt import create_access_token, create_refresh_token
from app.utils.hashing import verify_password
from app.utils.mail import mail_manager
from app.utils.utils import generate_invite_link
from app.settings import settings


router = APIRouter(prefix="/users")


@router.post("/sign_in")
def login_user(
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
    background_tasks: BackgroundTasks
):
    user = authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.status == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is Inactive"
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email}
    )

    background_tasks.add_task(mail_manager.send_login_alert, user.email)
    return schemas.Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/sign_up", status_code=status.HTTP_200_OK)
def registor_user(data: schemas.RegisterInput, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db=db, email=data.user.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_in_db = crud.create_user(db=db, user=data.user)
    organization = crud.create_organization(db, organization=data.organization)
    crud.create_membership_owner(
        db=db, org_id=organization.id, user_id=user_in_db.id)

    token = create_access_token(
        data={"sub": user_in_db.email}, expires_delta=timedelta(hours=2))
    crud.create_user_invitation(db=db, user_id=user_in_db.id, token=token)
    link = generate_invite_link(token=token)
    mail_manager.send_user_invite(
        to_address=user_in_db.email, invite_link=link)

    return schemas.DetailResponse(detail="User registration successful!")


@router.get("/invite")
def accept_user_invitation(
    token: str,
    db: Annotated[Session, Depends(get_db)]
):
    user_invitation = crud.get_user_invitation_by_token(db=db, token=token)
    if not user_invitation or user_invitation.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token.")
    if user_invitation.user.status == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already active.")

    crud.activate_user(db=db, user=user_invitation.user)
    crud.update_user_invitation_status(db=db, user_invitation=user_invitation)

    return schemas.DetailResponse(detail="User activation compleated.")


@router.post("/reset_password")
def reset_user_me_password(
        data: schemas.ResetPasswordInput,
        user: Annotated[UserModel, Depends(get_current_active_user)],
        db: Annotated[Session, Depends(get_db)]):
    if not verify_password(
        plain_password=data.old_password.get_secret_value(),
        hashed_password=user.password
    ):
        raise HTTPException(detail="Incorrect old password",
                            status_code=status.HTTP_400_BAD_REQUEST)
    crud.update_user_password(
        db=db, user=user, new_password=data.new_password.get_secret_value())
    mail_manager.send_password_update_alert(to_address=user.email)

    return schemas.DetailResponse(detail="User password reset successfully.")
