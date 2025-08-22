from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import EmailStr
from app.core.deps import get_db
from ...models import User
from ...utils.email import send_reset_email
import uuid
from ...core.security import get_password_hashed

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"]
)


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invlaid token"
        )
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified successfully"}


@router.post("/forgot_password")
async def forgot_password(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    token = str(uuid.uuid4())
    user.password_reset_token = token
    db.commit()

    await send_reset_email(user.email, token)
    return {"Message": "Reset email sent"}


@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.password_reset_token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    user.hashed_password = get_password_hashed(new_password)
    user.password_reset_token = None
    db.commit()
    return {"message": "Password reset successful"}
