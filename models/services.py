from sqlalchemy import Column, String, Integer, Numeric
from sqlalchemy.orm import relationship

from database import Base


class Service(Base):
    __tablename__ = "services"

    service_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    price = Column(Numeric(10, 2), nullable=False)
    duration = Column(Integer, nullable=False)

    appointments = relationship("Appointment", back_populates="service")
