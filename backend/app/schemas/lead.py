from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class LeadStatus(str, Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    unqualified = "unqualified"
    converted = "converted"
    lost = "lost"


class LeadSource(str, Enum):
    referral = "referral"
    ad = "ad"
    webform = "webform"
    cold_call = "cold_call"
    email = "email"
    social_media = "social_media"
    other = "other"


class LeadBase(BaseModel):
    name: str
    status: Optional[LeadStatus] = LeadStatus.new
    source: Optional[LeadSource] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(LeadBase):
    pass


class LeadOut(LeadBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class PaginatedLeadOut(BaseModel):
    total: int
    items: List[LeadOut]
