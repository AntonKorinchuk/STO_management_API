import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_async_db
from schemas.document import DocumentResponse, DocumentTypeEnum
from models.document import Document
from models.mechanic import Mechanic, MechanicRole
from crud.mechanic import get_current_mechanic


UPLOAD_DIRECTORY = "uploads/documents"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentTypeEnum = DocumentTypeEnum.PASSPORT,
    db: AsyncSession = Depends(get_async_db),
    current_mechanic: Mechanic = Depends(get_current_mechanic),
):
    """Uploads a document for the current mechanic."""

    allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png"}
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, detail="Invalid file type. Allowed types: PDF, JPG, PNG"
        )

    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    new_document = Document(
        mechanic_id=current_mechanic.mechanic_id,
        type=document_type,
        file_path=file_path,
    )

    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)

    return DocumentResponse(
        document_id=new_document.document_id,
        mechanic_id=new_document.mechanic_id,
        type=new_document.type,
        file_path=new_document.file_path,
    )


@router.get("/", response_model=List[DocumentResponse])
async def get_mechanic_documents(
    db: AsyncSession = Depends(get_async_db),
    current_mechanic: Mechanic = Depends(get_current_mechanic),
):
    """Fetches all documents for the current mechanic."""

    query = select(Document).where(Document.mechanic_id == current_mechanic.mechanic_id)
    result = await db.execute(query)
    documents = result.scalars().all()

    return [
        DocumentResponse(
            document_id=doc.document_id,
            mechanic_id=doc.mechanic_id,
            type=doc.type,
            file_path=doc.file_path,
        )
        for doc in documents
    ]


@router.get("/all", response_model=List[DocumentResponse])
async def get_all_documents(
    db: AsyncSession = Depends(get_async_db),
    current_mechanic: Mechanic = Depends(get_current_mechanic),
):
    """Fetches all documents; only administrators can access."""
    if current_mechanic.role != MechanicRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(Document)
    result = await db.execute(query)
    documents = result.scalars().all()

    return [
        DocumentResponse(
            document_id=doc.document_id,
            mechanic_id=doc.mechanic_id,
            type=doc.type,
            file_path=doc.file_path,
        )
        for doc in documents
    ]


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    file: UploadFile = File(...),
    document_type: DocumentTypeEnum = DocumentTypeEnum.PASSPORT,
    db: AsyncSession = Depends(get_async_db),
    current_mechanic: Mechanic = Depends(get_current_mechanic),
):
    """Updates a document's file and type; authorized mechanics or admins only."""
    query = select(Document).where(Document.document_id == document_id)
    result = await db.execute(query)
    existing_document = result.scalar_one_or_none()

    if not existing_document:
        raise HTTPException(status_code=404, detail="Document not found")

    if (
        existing_document.mechanic_id != current_mechanic.mechanic_id
        and current_mechanic.role != MechanicRole.ADMIN
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png"}
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, detail="Invalid file type. Allowed types: PDF, JPG, PNG"
        )

    if os.path.exists(existing_document.file_path):
        os.remove(existing_document.file_path)

    new_file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

    try:
        with open(new_file_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    existing_document.type = document_type
    existing_document.file_path = new_file_path

    await db.commit()
    await db.refresh(existing_document)

    return DocumentResponse(
        document_id=existing_document.document_id,
        mechanic_id=existing_document.mechanic_id,
        type=existing_document.type,
        file_path=existing_document.file_path,
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_mechanic: Mechanic = Depends(get_current_mechanic),
):
    """Deletes a document; authorized mechanics or admins only."""
    query = select(Document).where(Document.document_id == document_id)
    result = await db.execute(query)
    existing_document = result.scalar_one_or_none()

    if not existing_document:
        raise HTTPException(status_code=404, detail="Document not found")

    if (
        existing_document.mechanic_id != current_mechanic.mechanic_id
        and current_mechanic.role != MechanicRole.ADMIN
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    if os.path.exists(existing_document.file_path):
        os.remove(existing_document.file_path)

    await db.delete(existing_document)
    await db.commit()

    return {"detail": "Document deleted successfully"}
