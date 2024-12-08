from datetime import datetime
from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict


class CreateUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    hashed_password: str
    full_name: Annotated[str, MaxLen(30)]


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


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    hashed_password: str
    full_name: Annotated[str, MaxLen(30)]
    active: bool


class PasswordResetRequest(BaseModel):
    token: str
    new_password: str
