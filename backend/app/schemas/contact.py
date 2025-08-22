from pydantic import BaseModel, EmailStr
from typing import Optional,List
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import Query

class ContactStatus(str, Enum):
    new = "new"
    contacted = "contacted"
    won = "won"
    lost = "lost"

class ContactSource(str, Enum):
    referral = "referral"
    ad = "ad"
    webform = "webform"

class ContactBase(BaseModel):
    name:str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    source: Optional[ContactSource] = None
    status: Optional[ContactStatus] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

class ContactCreate(ContactBase):
    pass 

class ContactUpdate(ContactBase):
    pass 

class ContactOut(ContactBase):
    id: int
    owner_id: int 

    class Config:
        from_attributes = True

class PaginatedContactOut(BaseModel):
    total: int
    items: List[ContactOut]