from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
from datetime import date


class MechanicRoleEnum(str, Enum):
    ADMIN = "ADMIN"
    MECHANIC = "MECHANIC"


class MechanicBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    birth_date: date
    login: str = Field(..., min_length=3, max_length=50)
    role: MechanicRoleEnum = MechanicRoleEnum.MECHANIC
    position: str = Field(..., min_length=2, max_length=100)


class MechanicCreate(MechanicBase):
    password: str = Field(..., min_length=8)

    @validator("birth_date")
    def validate_birth_date(cls, v):
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("The mechanic must be over 18 years old")
        return v


class MechanicUpdate(BaseModel):
    name: Optional[str] = None
    birth_date: Optional[date] = None
    login: Optional[str] = None
    position: Optional[str] = None


class MechanicResponse(MechanicBase):
    mechanic_id: int

    class Config:
        from_attributes = True
