import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from crud.auth_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from database import get_async_db
from schemas.user import UserCreate, UserResponse, UserLogin, UserBase
from models.user import User, UserRole

router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)):
    """Retrieve the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    query = select(User).where(User.user_id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """Register a new user."""
    query = select(User).where(User.email == user.email)
    existing_user = await db.execute(query)

    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password.decode('utf-8'),
        role=user.role
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse(
        user_id=new_user.user_id,
        name=new_user.name,
        email=new_user.email,
        role=new_user.role,
        created_at=datetime.now()
    )

@router.post("/login")
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_async_db)):
    """Authenticate a user and return a JWT token."""
    query = select(User).where(User.email == user_login.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not bcrypt.checkpw(user_login.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get the details of the current authenticated user."""
    return UserResponse(
        user_id=current_user.user_id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        created_at=datetime.now()
    )

@router.get("/", response_model=List[UserResponse])
async def read_users(
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user)
):
    """Retrieve all users (admin-only)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()

    return [
        UserResponse(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=datetime.now()
        ) for user in users
    ]

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int,
        user_update: UserBase,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user)
):
    """Update a user's details."""
    if current_user.user_id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = update(User).where(User.user_id == user_id).values(
        name=user_update.name,
        email=user_update.email,
        role=user_update.role
    )

    result = await db.execute(query)
    await db.commit()

    query = select(User).where(User.user_id == user_id)
    result = await db.execute(query)
    updated_user = result.scalar_one_or_none()

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        user_id=updated_user.user_id,
        name=updated_user.name,
        email=updated_user.email,
        role=updated_user.role,
        created_at=datetime.now()
    )

@router.delete("/{user_id}")
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user)
):
    """Delete a user (admin or owner only)."""
    if current_user.user_id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = delete(User).where(User.user_id == user_id)
    result = await db.execute(query)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"detail": "User deleted successfully"}
