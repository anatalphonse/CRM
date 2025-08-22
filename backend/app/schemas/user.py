from pydantic import BaseModel,EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    user = "user"

class UserSchema(BaseModel):
    id: int
    name: str 
    email: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str
    email:EmailStr
    password: str
    role: Optional[UserRole] = UserRole.user

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None

class PaginatedUserOut(BaseModel):
    total: int
    items: List[UserSchema]