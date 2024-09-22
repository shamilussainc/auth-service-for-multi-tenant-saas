from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from app import schemas, crud
from app.models import User as UserModel, Member as MemberModel
from app.dependencies import get_db, get_current_active_user


router = APIRouter(prefix="/members")


@router.get("")
def get_user_organizations(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    organizations = crud.get_owner_organizations(
        db=db, user_id=current_user.id)
    resp_data = []
    for org in organizations:
        org_data = {
            "id": org.id,
            "name": org.name,
            "members": []
        }
        for member in org.members:
            member_data = {
                "id": member.id,
                "user": {
                    "id": member.user.id,
                    "email": member.user.email,
                },
                "role": {
                    "id": member.role.id,
                    "name": member.role.name
                }
            }
            org_data["members"].append(member_data)
        resp_data.append(org_data)

    return resp_data


@router.post("/invite")
def invite_member_to_organization(
    data: schemas.InviteMemberIn,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    current_user_member = crud.get_owner_membership(
        db=db, user_id=current_user.id, org_id=data.org_id)
    if not current_user_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action"
        )

    user = crud.get_user_by_email(db=db, email=data.user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found.")

    membership = crud.get_membership(
        db=db, user_id=user.id, org_id=data.org_id)
    if membership:
        if membership.status == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation already sent")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member.")

    crud.create_membership(db=db, org_id=data.org_id,
                           user_id=user.id, role="normal_user")

    return schemas.DetailResponse(detail="User invitation sent.")


@router.delete("/{member_id}")
def delete_member_from_organization(
        member_id: int, db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    member = crud.get_member_by_id(db=db, id=member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found."
        )
    if crud.get_owner_membership(db=db, user_id=current_user.id, org_id=member.org_id):
        crud.delete_member(db=db, member_id=member_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action"
        )
    return schemas.DetailResponse(detail="Member deleted.")


@router.post("/{member_id}/change_role")
def update_member_role(
    member_id: int,
    data: schemas.ChangeMemberRoleIn,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    member = crud.get_member_by_id(db=db, id=member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found."
        )
    if crud.get_owner_membership(db=db, user_id=current_user.id, org_id=member.org_id):
        crud.update_member_role(
            db=db, member_id=member_id, new_role=data.new_role)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action"
        )

    return schemas.DetailResponse(detail="Member role updated.")
