from typing import Optional

from pydantic import BaseModel, Field


class CarBase(BaseModel):
    brand: str = Field(..., min_length=2, max_length=100)
    model: str = Field(..., min_length=2, max_length=100)
    year: int = Field(..., ge=1900, le=2024)
    plate_number: str = Field(..., min_length=5, max_length=20)
    vin: str = Field(..., min_length=17, max_length=17)


class CarCreate(CarBase):
    user_id: int


class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    plate_number: Optional[str] = None
    vin: Optional[str] = None


class CarResponse(CarBase):
    car_id: int
    user_id: int

    class Config:
        from_attributes = True
