from enum import Enum
from typing import Any
from pydantic import BaseModel, EmailStr, SecretStr, Json, Field


class TokenType(Enum):
    ACCESS = 1
    REFRESH = 2


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1)


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr = Field(min_length=8)


class RegisterInput(BaseModel):
    user: UserCreate
    organization: OrganizationCreate


class DetailResponse(BaseModel):
    detail: str


class LoginInput(UserCreate):
    email: EmailStr
    password: SecretStr = Field(min_length=8)


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    email: str | None = None
    token_type: TokenType


class ResetPasswordInput(BaseModel):
    old_password: SecretStr = Field(min_length=8)
    new_password: SecretStr = Field(min_length=8)


class InviteMemberIn(BaseModel):
    user_email: EmailStr
    org_id: int
    role: str = Field(min_length=1)


class ChangeMemberRoleIn(BaseModel):
    new_role: str = Field(min_length=1)
