import bcrypt
import jwt
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from crud.auth_config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
)
from database import get_async_db
from models.mechanic import MechanicRole, Mechanic
from schemas.mechanic import (
    MechanicCreate,
    MechanicResponse,
    MechanicUpdate,
)
from models.appoinment import Appointment

router = APIRouter(prefix="/mechanics", tags=["mechanics"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="mechanic/token")


async def get_current_mechanic(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)
):
    """
    Validate token and retrieve the current mechanic.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mechanic_id: int = payload.get("sub")
        if mechanic_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    query = select(Mechanic).where(Mechanic.mechanic_id == mechanic_id)
    result = await db.execute(query)
    mechanic = result.scalar_one_or_none()

    if mechanic is None:
        raise credentials_exception

    return mechanic


@router.post("/register", response_model=MechanicResponse)
async def register_mechanic(
    mechanic: MechanicCreate, db: AsyncSession = Depends(get_async_db)
):
    """
    Register a new mechanic.
    """
    query = select(Mechanic).where(Mechanic.login == mechanic.login)
    existing_mechanic = await db.execute(query)

    if existing_mechanic.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Login already registered"
        )

    hashed_password = bcrypt.hashpw(mechanic.password.encode("utf-8"), bcrypt.gensalt())

    new_mechanic = Mechanic(
        name=mechanic.name,
        birth_date=mechanic.birth_date,
        login=mechanic.login,
        password=hashed_password.decode("utf-8"),
        role=mechanic.role,
        position=mechanic.position,
    )

    db.add(new_mechanic)
    await db.commit()
    await db.refresh(new_mechanic)

    return MechanicResponse(
        mechanic_id=new_mechanic.mechanic_id,
        name=new_mechanic.name,
        birth_date=new_mechanic.birth_date,
        login=new_mechanic.login,
        role=new_mechanic.role,
        position=new_mechanic.position,
    )


@router.post("/login")
async def login_mechanic(
    login: str, password: str, db: AsyncSession = Depends(get_async_db)
):
    """
    Authenticate a mechanic and return an access token.
    """
    query = select(Mechanic).where(Mechanic.login == login)
    result = await db.execute(query)
    mechanic = result.scalar_one_or_none()

    if not mechanic or not bcrypt.checkpw(
        password.encode("utf-8"), mechanic.password.encode("utf-8")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(mechanic.mechanic_id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "mechanic_id": mechanic.mechanic_id,
        "role": mechanic.role,
    }


@router.get("/me", response_model=MechanicResponse)
async def read_mechanic_me(current_mechanic: Mechanic = Depends(get_current_mechanic)):
    """
    Get details of the currently logged-in mechanic.
    """
    return MechanicResponse(
        mechanic_id=current_mechanic.mechanic_id,
        name=current_mechanic.name,
        birth_date=current_mechanic.birth_date,
        login=current_mechanic.login,
        role=current_mechanic.role,
        position=current_mechanic.position,
    )


@router.get("/", response_model=List[MechanicResponse])
async def read_mechanics(
    db: AsyncSession = Depends(get_async_db),
    current_mechanic: Mechanic = Depends(get_current_mechanic),
):
    """
    Get a list of all mechanics (Admin only).
    """
    if current_mechanic.role != MechanicRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(Mechanic)
    result = await db.execute(query)
    mechanics = result.scalars().all()

    return [
        MechanicResponse(
            mechanic_id=mechanic.mechanic_id,
            name=mechanic.name,
            birth_date=mechanic.birth_date,
            login=mechanic.login,
            role=mechanic.role,
            position=mechanic.position,
        )
        for mechanic in mechanics
    ]


@router.put("/{mechanic_id}", response_model=MechanicResponse)
async def update_mechanic(
    mechanic_id: int,
    mechanic_update: MechanicUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_mechanic: Mechanic = Depends(get_current_mechanic),
):
    """
    Update mechanic details (self or Admin only).
    """
    if (
        current_mechanic.mechanic_id != mechanic_id
        and current_mechanic.role != MechanicRole.ADMIN
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = {k: v for k, v in mechanic_update.dict().items() if v is not None}

    query = (
        update(Mechanic)
        .where(Mechanic.mechanic_id == mechanic_id)
        .values(**update_data)
    )
    await db.execute(query)
    await db.commit()

    query = select(Mechanic).where(Mechanic.mechanic_id == mechanic_id)
    result = await db.execute(query)
    updated_mechanic = result.scalar_one_or_none()

    if not updated_mechanic:
        raise HTTPException(status_code=404, detail="Mechanic not found")

    return MechanicResponse(
        mechanic_id=updated_mechanic.mechanic_id,
        name=updated_mechanic.name,
        birth_date=updated_mechanic.birth_date,
        login=updated_mechanic.login,
        role=updated_mechanic.role,
        position=updated_mechanic.position,
    )


@router.delete("/{mechanic_id}")
async def delete_mechanic(
    mechanic_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_mechanic: Mechanic = Depends(get_current_mechanic),
):
    """
    Delete a mechanic (Admin only).
    """
    if current_mechanic.role != MechanicRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = delete(Mechanic).where(Mechanic.mechanic_id == mechanic_id)
    result = await db.execute(query)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Mechanic not found")

    return {"detail": "Mechanic deleted successfully"}


@router.get("/appointments", response_model=List[dict])
async def get_mechanic_appointments(
    db: AsyncSession = Depends(get_async_db),
    current_mechanic: Mechanic = Depends(get_current_mechanic),
):
    """
    Get appointments for the currently logged-in mechanic.
    """
    query = select(Appointment).where(
        Appointment.mechanic_id == current_mechanic.mechanic_id
    )
    result = await db.execute(query)
    appointments = result.scalars().all()

    return [
        {
            "appointment_id": appt.appointment_id,
            "car_id": appt.car_id,
            "service_type": appt.service_type,
            "appointment_date": appt.appointment_date,
            "status": appt.status,
        }
        for appt in appointments
    ]
