from typing import List
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from database import get_async_db
from models.services import Service
from schemas.services import ServiceCreate, ServiceResponse, ServiceUpdate
from models.user import User, UserRole
from crud.user import get_current_user

router = APIRouter(prefix="/services", tags=["services"])


@router.post("/", response_model=ServiceResponse)
async def create_service(
    service: ServiceCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):

    """Creates a new service; only administrators can perform this action."""

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only administrators can create services"
        )

    query = select(Service).where(Service.name == service.name)
    existing_service = await db.execute(query)

    if existing_service.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service with this name already exists",
        )

    new_service = Service(
        name=service.name,
        description=service.description,
        price=service.price,
        duration=service.duration,
    )

    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)

    return ServiceResponse(
        service_id=new_service.service_id,
        name=new_service.name,
        description=new_service.description,
        price=new_service.price,
        duration=new_service.duration,
    )


@router.get("/", response_model=List[ServiceResponse])
async def read_services(db: AsyncSession = Depends(get_async_db)):

    """Fetches a list of all available services."""

    query = select(Service)
    result = await db.execute(query)
    services = result.scalars().all()

    return [
        ServiceResponse(
            service_id=service.service_id,
            name=service.name,
            description=service.description,
            price=service.price,
            duration=service.duration,
        )
        for service in services
    ]


@router.get("/{service_id}", response_model=ServiceResponse)
async def read_service(service_id: int, db: AsyncSession = Depends(get_async_db)):

    query = select(Service).where(Service.service_id == service_id)
    result = await db.execute(query)
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return ServiceResponse(
        service_id=service.service_id,
        name=service.name,
        description=service.description,
        price=service.price,
        duration=service.duration,
    )


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    service_update: ServiceUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Updates a service by its ID; only administrators can perform this action."""

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only administrators can update services"
        )

    update_data = {k: v for k, v in service_update.dict().items() if v is not None}

    query = select(Service).where(Service.service_id == service_id)
    existing_service = await db.execute(query)

    if not existing_service.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Service not found")

    if "name" in update_data:
        name_query = select(Service).where(Service.name == update_data["name"])
        existing_name = await db.execute(name_query)

        if existing_name.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service with this name already exists",
            )

    query = (
        update(Service).where(Service.service_id == service_id).values(**update_data)
    )
    await db.execute(query)
    await db.commit()

    query = select(Service).where(Service.service_id == service_id)
    result = await db.execute(query)
    updated_service = result.scalar_one_or_none()

    return ServiceResponse(
        service_id=updated_service.service_id,
        name=updated_service.name,
        description=updated_service.description,
        price=updated_service.price,
        duration=updated_service.duration,
    )


@router.delete("/{service_id}")
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """Deletes a service by its ID; only administrators can perform this action."""

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only administrators can delete services"
        )

    query = select(Service).where(Service.service_id == service_id)
    existing_service = await db.execute(query)

    if not existing_service.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Service not found")

    query = delete(Service).where(Service.service_id == service_id)
    result = await db.execute(query)
    await db.commit()

    return {"detail": "Service deleted successfully"}


@router.get("/search", response_model=List[ServiceResponse])
async def search_services(
    name: str = None,
    min_price: Decimal = None,
    max_price: Decimal = None,
    db: AsyncSession = Depends(get_async_db),
):

    """Searches for services by name and/or price range."""

    query = select(Service)

    if name:
        query = query.where(Service.name.ilike(f"%{name}%"))

    if min_price is not None:
        query = query.where(Service.price >= min_price)

    if max_price is not None:
        query = query.where(Service.price <= max_price)

    result = await db.execute(query)
    services = result.scalars().all()

    return [
        ServiceResponse(
            service_id=service.service_id,
            name=service.name,
            description=service.description,
            price=service.price,
            duration=service.duration,
        )
        for service in services
    ]
