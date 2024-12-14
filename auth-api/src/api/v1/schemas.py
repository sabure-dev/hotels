from datetime import datetime
from enum import Enum
from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict


class UserRole(str, Enum):
    BUYER = 'buyer'
    SELLER = 'seller'
    ADMIN = 'admin'


class CreateUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    hashed_password: str
    full_name: Annotated[str, MaxLen(30)]
    role: UserRole


class ValidateUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    hashed_password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: Annotated[str, MaxLen(30)]
    created_at: datetime
    is_verified: bool
    active: bool


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    hashed_password: str
    full_name: Annotated[str, MaxLen(30)]
    active: bool
    is_verified: bool


class PasswordResetRequest(BaseModel):
    token: str
    new_password: str
