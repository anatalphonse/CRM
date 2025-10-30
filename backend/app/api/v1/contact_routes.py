from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.deps import get_db
from app import schemas, models, services
from app.core.security import get_current_user
from fastapi import Query
from typing import Optional, List
from app.models.contact import Contact
from sqlalchemy import desc, asc, func
from datetime import datetime


router = APIRouter()


@router.post("", response_model=schemas.contact.ContactOut)
async def create_contact(
    contact: schemas.contact.ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_contact = models.Contact(**contact.dict(), owner_id=current_user.id)
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact


@router.get("", response_model=schemas.contact.PaginatedContactOut)
async def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    sort_by: Optional[str] = Query("id"),
    sort_order: Optional[str] = Query("asc"),
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    q: Optional[str] = Query(None, description="full-text search query"),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # query = db.query(models.Contact).filter(models.Contact.owner_id == current_user.id)
    query = select(models.Contact).where(
        models.Contact.owner_id == current_user.id)

    # Filter
    if status:
        query = query.where(models.Contact.status == status)
    if source:
        query = query.where(models.Contact.source == source)
    if start_date and end_date:
        query = query.where(
            models.Contact.created_at.between(start_date, end_date))

    # Global Search
    if q:
        contacts = await services.user_service.search_contacts_fuzzy(db, q, skip, limit)
        total = len(contacts)
        return {"total": total, "items": contacts}

    # Sorting
    sort_column = getattr(models.Contact, sort_by, models.Contact.id)
    query = query.order_by(
        desc(sort_column)) if sort_order == "desc" else query.order_by(asc(sort_column))

    # Get total count
    count_query = select(func.count()).select_from(query)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get users
    paginated_query = query.offset(skip).limit(limit)
    result = await db.execute(paginated_query)
    contacts = result.scalars().all()

    return {"total": total, "items": contacts}


@router.put("/{contact_id}", response_model=schemas.ContactOut)
async def update_contact(
    contact_id: int,
    updated_contact: schemas.contact.ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(select(models.Contact).where(
        id=contact_id, owner_id=current_user.id))

    contact = result.scalar()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    for key, value in updated_contact.dict(exclude_unset=True).items():
        setattr(contact, key, value)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    contact = db.query(Contact).filter_by(
        id=contact_id, owner_id=current_user.id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    db.delete(contact)
    db.commit()
    return {"detail": "Contact deleted"}
