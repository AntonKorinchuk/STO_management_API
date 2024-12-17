from pydantic import BaseModel, Field
from enum import Enum


class DocumentTypeEnum(str, Enum):
    PASSPORT = "PASSPORT"
    TAX_ID = "TAX_ID"
    DIPLOMA = "DIPLOMA"
    EMPLOYMENT_CONTRACT = "EMPLOYMENT_CONTRACT"


class DocumentBase(BaseModel):
    type: DocumentTypeEnum
    file_path: str = Field(..., min_length=1, max_length=255)


class DocumentCreate(DocumentBase):
    mechanic_id: int


class DocumentResponse(DocumentBase):
    document_id: int
    mechanic_id: int

    class Config:
        from_attributes = True
