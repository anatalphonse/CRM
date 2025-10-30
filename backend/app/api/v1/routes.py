from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.deps import get_db
from app.models.user import User
from app.schemas.user import UserSchema
from typing import List
from app import schemas, services, models
from app.core.security import create_access_token, get_current_user
from app.utils.email import send_verification_email
import asyncio


router = APIRouter()


@router.get("/users", response_model=List[UserSchema])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.post("/register", response_model=schemas.UserSchema)
async def register_user(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Database operations (~100-200ms)
    result = await db.execute(
        select(models.user.User).where(models.user.User.email == user_in.email)
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = await services.user_service.create_user(db, user_in)
    token = str(user.verification_token)

    # Fire and forget email ✅
    asyncio.create_task(send_verification_email(user.email, token))

    # Return immediately
    return user


@router.post("/login", response_model=schemas.Token)
async def login(user_in: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    user = await services.user_service.authenticate_user(
        db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid email or password"
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your Email"
        )
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserSchema)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=schemas.UserUpdate)
async def update_my_profile(
    update_data: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    updated_user = await services.user_service.update_user(
        db, current_user, update_data)
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    await services.user_service.delete_user(db, current_user)
    return
