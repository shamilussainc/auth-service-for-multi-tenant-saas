from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    BigInteger,
    JSON,
    ForeignKey,
    UniqueConstraint,
    ForeignKeyConstraint,
    func
)
from sqlalchemy.orm import mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, unique=False, nullable=False)
    profile = Column(JSON, default={}, nullable=False)
    status = Column(Integer, default=0, nullable=False)
    settings = Column(JSON, default={}, nullable=True)
    created_at = Column(BigInteger, nullable=True)
    updated_at = Column(BigInteger, nullable=True)

    memberships = relationship("Member", back_populates="user")
    user_invitations = relationship("UserInvitation", back_populates="user")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(Integer, default=0, nullable=False)
    personal = Column(Boolean, default=False, nullable=True)
    settings = Column(JSON, default={}, nullable=True)
    created_at = Column(BigInteger, nullable=True)
    updated_at = Column(BigInteger, nullable=True)

    members = relationship("Member", back_populates="organization")


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("name", "org_id", name="unique_role_in_org"),
        UniqueConstraint("id", "org_id", name="unique_id_org_id"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    org_id = mapped_column(ForeignKey(
        "organizations.id", ondelete="CASCADE"), nullable=False)

    members = relationship("Member", back_populates="role",
                           foreign_keys="[Member.role_id]")


class Member(Base):
    __tablename__ = "member"
    __table_args__ = (
        UniqueConstraint("org_id", "user_id", name="unique_org_id_user_id"),
        ForeignKeyConstraint(
            ["role_id", "org_id"],
            ["roles.id", "roles.org_id"])
    )

    id = Column(Integer, primary_key=True)
    org_id = mapped_column(ForeignKey(
        "organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    role_id = mapped_column(ForeignKey(
        "roles.id", ondelete="CASCADE"), nullable=False)
    status = Column(Integer, nullable=False, default=0)
    settings = Column(JSON, default={}, nullable=True)
    created_at = Column(BigInteger, nullable=True)
    updated_at = Column(BigInteger, nullable=True)

    organization = relationship(Organization, back_populates="members")
    user = relationship(User, back_populates="memberships")
    role = relationship(Role, back_populates="members", foreign_keys=[role_id])


class UserInvitation(Base):
    __tablename__ = "user_invitations"

    id = Column(Integer, primary_key=True)
    user_id = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, nullable=False, index=True)
    is_used = Column(Boolean, default=False, nullable=False)

    created_at = Column(BigInteger, nullable=True)
    expires_at = Column(BigInteger, nullable=True)

    user = relationship(User, back_populates="user_invitations")
