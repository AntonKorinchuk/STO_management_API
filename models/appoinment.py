from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum


class AppointmentStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    car_id = Column(Integer, ForeignKey('cars.car_id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.service_id'), nullable=False)
    mechanic_id = Column(Integer, ForeignKey('mechanics.mechanic_id'), nullable=True)
    appointment_date = Column(DateTime, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)

    user = relationship("User", back_populates="appointments")
    car = relationship("Car", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    mechanic = relationship("Mechanic", back_populates="appointments")
