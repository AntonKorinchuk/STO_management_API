from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum


class DocumentType(enum.Enum):
    PASSPORT = "PASSPORT"
    TAX_ID = "TAX_ID"
    DIPLOMA = "DIPLOMA"
    EMPLOYMENT_CONTRACT = "EMPLOYMENT_CONTRACT"


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, index=True)
    mechanic_id = Column(Integer, ForeignKey("mechanics.mechanic_id"), nullable=False)
    type = Column(Enum(DocumentType), nullable=False)
    file_path = Column(String(255), nullable=False)

    mechanic = relationship("Mechanic", back_populates="documents")
