import enum
from sqlalchemy import Column, Integer, String, Date, Enum
from sqlalchemy.orm import relationship

from database import Base


class MechanicRole(enum.Enum):
    ADMIN = "admin"
    MECHANIC = "mechanic"


class Mechanic(Base):
    __tablename__ = "mechanics"

    mechanic_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=False)
    login = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(MechanicRole), nullable=False, default=MechanicRole.MECHANIC)
    position = Column(String(100), nullable=False)

    documents = relationship("Document", back_populates="mechanic")
    appointments = relationship("Appointment", back_populates="mechanic")
