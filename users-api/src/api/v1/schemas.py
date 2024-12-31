from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class RoleSchema(BaseModel):
    id: int
    title: str
    description: str


class UserRole(str, Enum):
    SELLER = "seller"
    ADMIN = "admin"
    BUYER = "buyer"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class CreateUser(UserBase):
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.BUYER


class UserSchema(UserBase):
    id: int
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True


class UserOut(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    role_id: int

    class Config:
        from_attributes = True


class PasswordResetRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
