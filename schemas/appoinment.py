from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, model_validator


class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELED = "canceled"


class AppointmentBase(BaseModel):
    user_id: int
    car_id: int
    service_id: int
    mechanic_id: Optional[int] = None
    appointment_date: datetime
    status: AppointmentStatus = AppointmentStatus.PENDING

    @model_validator(mode="before")
    @classmethod
    def validate_date(cls, values):
        appointment_date = values.get("appointment_date")
        if appointment_date and appointment_date <= datetime.now(timezone.utc):
            raise ValueError("Appointment date must be in the future.")
        return values

    class Config:
        from_attributes = True


class AppointmentCreate(AppointmentBase):
    status: Optional[AppointmentStatus] = AppointmentStatus.PENDING


class AppointmentResponse(AppointmentBase):
    appointment_id: int


class AppointmentUpdate(BaseModel):
    user_id: Optional[int] = None
    car_id: Optional[int] = None
    service_id: Optional[int] = None
    mechanic_id: Optional[int] = None
    appointment_date: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None

    @model_validator(mode="before")
    @classmethod
    def validate_date(cls, values):
        appointment_date = values.get("appointment_date")
        if appointment_date and appointment_date <= datetime.now(timezone.utc):
            raise ValueError("Appointment date must be in the future.")
        return values
