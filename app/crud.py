from sqlalchemy import func
from sqlalchemy.orm import Session
from app.utils.hashing import get_password_hash
from app.models import User, Organization, Member, Role, UserInvitation
from app import schemas


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).where(User.email == email).first()


def get_user_by_id(db: Session, id: int) -> User | None:
    return db.query(User).where(User.id == id).first()


def create_user(db: Session, user: schemas.UserCreate) -> User:
    user_db = User()
    user_db.email = user.email
    user_db.password = get_password_hash(
        password=user.password.get_secret_value())

    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    return user_db


def update_user_password(db: Session, user: User, new_password: str):
    user.password = get_password_hash(password=new_password)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def activate_user(db: Session, user: User):
    user.status = 1
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def create_user_invitation(db: Session, user_id: int, token: str):
    user_invitation = UserInvitation(user_id=user_id, token=token)
    db.add(user_invitation)
    db.commit()
    db.refresh(user_invitation)

    return user_invitation


def get_user_invitation_by_token(db: Session, token: str):
    return db.query(UserInvitation).where(UserInvitation.token == token).first()


def update_user_invitation_status(db: Session, user_invitation: UserInvitation):
    user_invitation.is_used = True
    db.add(user_invitation)
    db.commit()
    db.refresh(user_invitation)

    return user_invitation


def create_organization(db: Session, organization: schemas.OrganizationCreate):
    db_organization = Organization(name=organization.name)
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)

    return db_organization


def get_owner_organizations(db: Session, user_id: int):
    organizations = db.query(Organization).join(Member).join(Role, Member.role_id == Role.id).filter(
        Member.user_id == user_id,
        Role.name == "owner"
    ).all()
    return organizations


def get_or_create_role(db: Session, org_id: int, role_name: str):
    role_obj = db.query(Role).filter(
        Role.name == role_name,
        Role.org_id == org_id).first()
    if not role_obj:
        role_obj = Role(name=role_name, org_id=org_id)
        db.add(role_obj)
        db.commit()
        db.refresh(role_obj)

    return role_obj


def create_membership(db: Session, org_id: int, user_id: int, role: str):
    role_obj = get_or_create_role(db=db, org_id=org_id, role_name=role)
    member = Member(org_id=org_id, user_id=user_id, role_id=role_obj.id)
    db.add(member)
    db.commit()
    db.refresh(member)

    return member


def create_membership_owner(db: Session, org_id: int, user_id: int):
    role = get_or_create_role(db=db, org_id=org_id, role_name="owner")
    member = Member(org_id=org_id, user_id=user_id, role_id=role.id)

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


def get_member_by_id(db: Session, id: int) -> Member:
    return db.query(Member).where(Member.id == id).first()


def update_member_role(db: Session, member: Member, new_role: str):
    role = db.query(Role).where(
        Role.name == new_role and Role.org_id == Member.org_id).first()
    if not role:
        role = Role()
        role.name = new_role
        role.org_id = member.org_id

        db.add(role)
        db.commit()
        db.refresh(role)

    member.role_id = role.id

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


def delete_member(db: Session, member: Member):
    db.delete(member)
    db.commit()


def get_membership(db: Session, user_id: int, org_id: int) -> Member:
    return db.query(Member).where(
        Member.user_id == user_id,
        Member.org_id == org_id,
    ).first()


def get_owner_membership(db: Session, user_id: int, org_id: int) -> Member:
    return db.query(Member).join(Role, Role.id == Member.role_id).filter(
        Member.user_id == user_id,
        Member.org_id == org_id,
        Role.name == "owner"
    ).first()


def get_role_wise_user_count(db: Session):
    return db.query(Role.name, func.count(Member.id)).join(Member, Member.role_id == Role.id).group_by(Role.name).all()


def get_org_wise_user_count(db: Session):
    return db.query(
        Organization,
        func.count(Member.id)
    ).join(
        Member, Member.org_id == Organization.id
    ).group_by(Organization.id)


def get_org_wise_role_wise_count(db: Session):
    result = db.query(
        Organization,
        Role,
        func.count(Member.id)
    ).join(
        Member, Member.org_id == Organization.id
    ).join(
        Role, Role.id == Member.role_id
    ).group_by(Organization.id, Role.id).all()

    role = Role()

    id_to_org_map = {}
    for org, role, user_count in result:
        role_out = schemas.RoleIdWiseCountOut(
            id=role.id,
            name=role.name,
            user_count=user_count
        )
        if org.id not in id_to_org_map:
            org_out = schemas.OrgWiseRoleWiseCountOut(
                id=org.id,
                name=org.name,
                roles=[]
            )
            id_to_org_map[org.id] = org_out
        id_to_org_map[org.id].roles.append(role_out)

    return [dict(value) for value in id_to_org_map.values()]
