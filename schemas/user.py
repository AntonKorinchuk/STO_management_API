from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role: UserRoleEnum = UserRoleEnum.CUSTOMER


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserResponse(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str
