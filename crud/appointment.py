import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_async_db
from models import Mechanic
from models.mechanic import MechanicRole
from models.services import Service
from models.appoinment import Appointment
from models.car import Car
from schemas.appoinment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
    AppointmentStatus
)
from models.user import User
from crud.user import get_current_user
from crud.mechanic import get_current_mechanic

# Email sending (async)
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

# Email Configuration
conf = ConnectionConfig(
    MAIL_USERNAME="your_username",
    MAIL_PASSWORD="your_password",
    MAIL_FROM="your_email@example.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="Car Service",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


async def send_appointment_confirmation_email(email: EmailStr, appointment_details: dict):
    """
    Асинхронна функція для надсилання електронної пошти про підтвердження запису
    """
    message = MessageSchema(
        subject="Appointment Confirmation",
        recipients=[email],
        body=f"""
        Appointment Details:
        - Date: {appointment_details['appointment_date']}
        - Service: {appointment_details.get('service_name', 'N/A')}
        - Status: {appointment_details['status']}

        Thank you for choosing our service!
        """,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)


router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
        appointment: AppointmentCreate,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user)
):
    """
    Створення нового запису на обслуговування
    """
    # Перевірка, чи належить автомобіль поточному користувачу
    car_query = select(Car).where(
        (Car.car_id == appointment.car_id) &
        (Car.user_id == current_user.user_id)
    )
    car_result = await db.execute(car_query)
    if not car_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only book appointments for your own cars"
        )

    # Перевірка наявності послуги
    service_query = select(Service).where(Service.service_id == appointment.service_id)
    service_result = await db.execute(service_query)
    service = service_result.scalar_one_or_none()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    # Створення запису
    new_appointment = Appointment(
        user_id=current_user.user_id,
        car_id=appointment.car_id,
        service_id=appointment.service_id,
        appointment_date=appointment.appointment_date,
        status=appointment.status or AppointmentStatus.PENDING
    )

    db.add(new_appointment)
    await db.commit()
    await db.refresh(new_appointment)

    # Асинхронна відправка email (у фоновому режимі)
    asyncio.create_task(send_appointment_confirmation_email(
        current_user.email,
        {
            'appointment_date': new_appointment.appointment_date,
            'service_name': service.name if service else 'Unknown Service',
            'status': new_appointment.status
        }
    ))

    return AppointmentResponse(
        appointment_id=new_appointment.appointment_id,
        user_id=new_appointment.user_id,
        car_id=new_appointment.car_id,
        service_id=new_appointment.service_id,
        appointment_date=new_appointment.appointment_date,
        status=new_appointment.status
    )


@router.get("/", response_model=List[AppointmentResponse])
async def get_user_appointments(
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user)
):
    """
    Отримання списку записів поточного користувача
    """
    query = select(Appointment).where(Appointment.user_id == current_user.user_id)
    result = await db.execute(query)
    appointments = result.scalars().all()

    return [
        AppointmentResponse(
            appointment_id=appt.appointment_id,
            user_id=appt.user_id,
            car_id=appt.car_id,
            service_id=appt.service_id,
            mechanic_id=appt.mechanic_id,
            appointment_date=appt.appointment_date,
            status=appt.status
        ) for appt in appointments
    ]


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
        appointment_id: int,
        appointment_update: AppointmentUpdate,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user)
):
    """
    Оновлення запису на обслуговування
    """
    # Перевірка наявності запису та прав користувача
    query = select(Appointment).where(
        (Appointment.appointment_id == appointment_id) &
        (Appointment.user_id == current_user.user_id)
    )
    result = await db.execute(query)
    existing_appointment = result.scalar_one_or_none()

    if not existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # Заборона оновлення завершених або скасованих записів
    if existing_appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update completed or canceled appointments"
        )

    # Підготовка даних для оновлення
    update_data = appointment_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(existing_appointment, key, value)

    db.add(existing_appointment)
    await db.commit()
    await db.refresh(existing_appointment)

    return AppointmentResponse(
        appointment_id=existing_appointment.appointment_id,
        user_id=existing_appointment.user_id,
        car_id=existing_appointment.car_id,
        service_id=existing_appointment.service_id,
        mechanic_id=existing_appointment.mechanic_id,
        appointment_date=existing_appointment.appointment_date,
        status=existing_appointment.status
    )


@router.delete("/{appointment_id}")
async def cancel_appointment(
        appointment_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user)
):
    """
    Скасування запису на обслуговування
    """
    # Перевірка наявності запису та прав користувача
    query = select(Appointment).where(
        (Appointment.appointment_id == appointment_id) &
        (Appointment.user_id == current_user.user_id)
    )
    result = await db.execute(query)
    existing_appointment = result.scalar_one_or_none()

    if not existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # Заборона скасування завершених записів
    if existing_appointment.status == AppointmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed appointments"
        )

    # Оновлення статусу на "скасовано"
    existing_appointment.status = AppointmentStatus.CANCELED

    db.add(existing_appointment)
    await db.commit()

    return {"detail": "Appointment canceled successfully"}


@router.put("/{appointment_id}/assign-mechanic")
async def assign_mechanic_to_appointment(
        appointment_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_mechanic: Mechanic = Depends(get_current_mechanic)
):
    """
    Призначення механіка для запису на обслуговування
    """
    # Перевірка наявності запису та прав механіка
    if current_mechanic.role != MechanicRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can assign mechanics"
        )

    query = select(Appointment).where(Appointment.appointment_id == appointment_id)
    result = await db.execute(query)
    existing_appointment = result.scalar_one_or_none()

    if not existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # Призначення механіка
    existing_appointment.mechanic_id = current_mechanic.mechanic_id
    existing_appointment.status = AppointmentStatus.CONFIRMED

    db.add(existing_appointment)
    await db.commit()
    await db.refresh(existing_appointment)

    return {
        "detail": "Mechanic assigned successfully",
        "appointment_id": existing_appointment.appointment_id,
        "mechanic_id": existing_appointment.mechanic_id
    }
