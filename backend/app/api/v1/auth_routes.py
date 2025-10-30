from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from app.core.deps import get_db
from ...models import User
from ...utils.email import send_reset_email
import uuid
from ...core.security import get_password_hashed
import asyncio


router = APIRouter()


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.verification_token == token))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    user.is_verified = True
    user.verification_token = None

    await db.commit()

    return {"message": "Email verified successfully"}


@router.post("/forgot_password")
async def forgot_password(email: EmailStr, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    token = str(uuid.uuid4())
    user.password_reset_token = token
    await db.commit()

    # Fire and forget email ✅
    asyncio.create_task(send_reset_email(user.email, token))

    return {"Message": "Reset email sent"}


@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.password_reset_token == token))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    user.hashed_password = get_password_hashed(new_password)
    user.password_reset_token = None
    await db.commit()
    return {"message": "Password reset successful"}
