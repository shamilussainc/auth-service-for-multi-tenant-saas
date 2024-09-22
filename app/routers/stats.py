from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud
from app.dependencies import get_db

router = APIRouter(prefix="/stats")


@router.get("/role-wise-users")
def role_wise_number_of_users(db: Annotated[Session, Depends(get_db)]):
    result = crud.get_role_wise_user_count(db=db)
    return [{"role": item[0], "user_count": item[1]} for item in result]


@router.get("/org-wise-users")
def organization_wise_number_of_users(db: Annotated[Session, Depends(get_db)]):
    result = crud.get_org_wise_user_count(db=db)
    return [{"organization": item[0], "user_count": item[1]} for item in result]


@router.get("/org-role-wise-users")
def organisation_wise_role_wise_number_of_users(db: Annotated[Session, Depends(get_db)]):
    result = crud.get_org_wise_role_wise_count(db=db)
    return result
