from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    price: Decimal = Field(..., gt=0)
    duration: int = Field(..., gt=0)


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    duration: Optional[int] = None


class ServiceResponse(ServiceBase):
    service_id: int

    class Config:
        from_attributes = True
