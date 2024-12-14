import enum

from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from database import Base


class UserRole(enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)

    cars = relationship("Car", back_populates="owner")
    appointments = relationship("Appointment", back_populates="user")

