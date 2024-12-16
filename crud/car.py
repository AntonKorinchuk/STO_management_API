from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


from database import get_async_db
from crud.user import get_current_user
from models.user import User
from schemas.car import CarCreate, CarUpdate, CarResponse
from models.car import Car

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post("/", response_model=CarResponse)
async def create_car(
    car: CarCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new car after checking VIN, plate number, and user access.
    """
    vin_check = await db.execute(select(Car).where(Car.vin == car.vin))
    plate_check = await db.execute(
        select(Car).where(Car.plate_number == car.plate_number)
    )

    if vin_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="VIN already exists"
        )

    if plate_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plate number already exists",
        )

    if car.user_id != current_user.user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add cars to your own profile",
        )

    new_car = Car(
        user_id=car.user_id,
        brand=car.brand,
        model=car.model,
        year=car.year,
        plate_number=car.plate_number,
        vin=car.vin,
    )

    db.add(new_car)
    await db.commit()
    await db.refresh(new_car)

    return CarResponse(
        car_id=new_car.car_id,
        user_id=new_car.user_id,
        brand=new_car.brand,
        model=new_car.model,
        year=new_car.year,
        plate_number=new_car.plate_number,
        vin=new_car.vin,
    )


@router.get("/", response_model=List[CarResponse])
async def read_cars(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a list of cars, filtered by user role.
    """
    if current_user.role.value == "admin":
        query = select(Car)
    else:
        query = select(Car).where(Car.user_id == current_user.user_id)

    result = await db.execute(query)
    cars = result.scalars().all()

    return [
        CarResponse(
            car_id=car.car_id,
            user_id=car.user_id,
            brand=car.brand,
            model=car.model,
            year=car.year,
            plate_number=car.plate_number,
            vin=car.vin,
        )
        for car in cars
    ]


@router.get("/{car_id}", response_model=CarResponse)
async def read_car(
    car_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Car).where(Car.car_id == car_id)
    result = await db.execute(query)
    car = result.scalar_one_or_none()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    if car.user_id != current_user.user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this car",
        )

    return CarResponse(
        car_id=car.car_id,
        user_id=car.user_id,
        brand=car.brand,
        model=car.model,
        year=car.year,
        plate_number=car.plate_number,
        vin=car.vin,
    )


@router.put("/{car_id}", response_model=CarResponse)
async def update_car(
    car_id: int,
    car_update: CarUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update car details after checking uniqueness of VIN and plate number.
    """
    query = select(Car).where(Car.car_id == car_id)
    result = await db.execute(query)
    car = result.scalar_one_or_none()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    if car.user_id != current_user.user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own cars",
        )

    update_data = car_update.dict(exclude_unset=True)

    if "vin" in update_data:
        vin_check = await db.execute(
            select(Car).where((Car.vin == update_data["vin"]) & (Car.car_id != car_id))
        )
        if vin_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="VIN already exists"
            )

    if "plate_number" in update_data:
        plate_check = await db.execute(
            select(Car).where(
                (Car.plate_number == update_data["plate_number"])
                & (Car.car_id != car_id)
            )
        )
        if plate_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plate number already exists",
            )

    for key, value in update_data.items():
        setattr(car, key, value)

    await db.commit()
    await db.refresh(car)

    return CarResponse(
        car_id=car.car_id,
        user_id=car.user_id,
        brand=car.brand,
        model=car.model,
        year=car.year,
        plate_number=car.plate_number,
        vin=car.vin,
    )


@router.delete("/{car_id}")
async def delete_car(
    car_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a car if the user is the owner or an admin.
    """
    query = select(Car).where(Car.car_id == car_id)
    result = await db.execute(query)
    car = result.scalar_one_or_none()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    if car.user_id != current_user.user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own cars",
        )

    await db.delete(car)
    await db.commit()

    return {"detail": "Car deleted successfully"}
