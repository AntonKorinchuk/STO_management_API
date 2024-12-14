from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from database import Base


class Car(Base):
    __tablename__ = "cars"

    car_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    brand = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    plate_number = Column(String(20), unique=True, nullable=False)
    vin = Column(String(20), nullable=False, unique=True)

    owner = relationship("User", back_populates="cars")
    appointments = relationship("Appointment", back_populates="car")
