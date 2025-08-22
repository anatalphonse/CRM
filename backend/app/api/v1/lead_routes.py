from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app import models, schemas, services
from app.core.security import get_current_user
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func, or_, desc, asc

router = APIRouter(
    prefix="/leads",
    tags=["Leads"]
)


@router.post("", response_model=schemas.lead.LeadOut)
def create_lead(lead: schemas.lead.LeadCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_lead = models.Lead(**lead.dict(), owner_id=current_user.id)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


@router.get("", response_model=schemas.lead.PaginatedLeadOut)
def list_lead(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    sort_by: Optional[str] = Query("id"),
    sort_order: Optional[str] = Query("asc"),
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    q: Optional[str] = Query(None, description="search by names and notes"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Lead).filter(models.Lead.owner_id == current_user.id)

    # Filter
    if status:
        query = query.filter(models.Lead.status == status)
    if source:
        query = query.filter(models.Lead.source == source)
    if created_after:
        query = query.filter(models.Lead.created_at >= created_after)
    if created_before:
        created_before = created_before.replace(microsecond=0)
        query = query.filter(func.date(models.Lead.created_at) <= created_before.date())
    
    #Global Search
    if q:
        leads = services.user_service.search_leads_fuzzy(db, q, skip, limit)
        total = len(leads)
        return {"total": total, "items": leads}
    
    # Sorting
    sort_column = getattr(models.Lead, sort_by, models.Lead.id)
    query = query.order_by(desc(sort_column)) if sort_order == "desc" else query.order_by(asc(sort_column))

    # Pagination
    total = query.count()
    leads = query.offset(skip).limit(limit).all()

    return {"total": total, "items": leads}

@router.get("/search", response_model=List[schemas.lead.LeadOut])
def search_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Lead).filter(
        models.Lead.owner_id == current_user.id)
    if name:
        query = query.filter(models.Lead.name.ilike(f"%{name}"))
    if status:
        query = query.filter(models.Lead.status == status)
    if source:
        query = query.filter(models.Lead.source.ilike(f"%{source}"))
    return query.offset(skip).limit(limit).all()


@router.put("/{lead_id}", response_model=schemas.lead.LeadOut)
def update_lead(
    lead_id: int,
    updated_lead: schemas.lead.LeadUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    lead = db.query(models.Lead).filter_by(
        id=lead_id, owner_id=current_user.id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    for key, value in updated_lead.dict(exclude_unset=True).items():
        setattr(lead, key, value)
        db.commit()
        db.refresh(lead)
        return lead

@router.delete("/{lead_id}")
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    lead = db.query(models.Lead).filter_by(id=lead_id, owner_id=current_user.id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    db.delete(lead)
    db.commit()
    return {"detail": "Lead deleted"}