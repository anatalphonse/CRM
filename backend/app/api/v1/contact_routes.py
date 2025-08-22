from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app import schemas, models, services
from app.core.security import get_current_user
from fastapi import  Query
from typing import Optional, List
from app.models.contact import Contact
from sqlalchemy import desc, asc
from datetime import datetime


router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"]
)


@router.post("", response_model=schemas.contact.ContactOut)
def create_contact(contact: schemas.contact.ContactCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_contact = models.Contact(**contact.dict(), owner_id=current_user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.get("", response_model=schemas.contact.PaginatedContactOut)
def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    sort_by: Optional[str] = Query("id"),
    sort_order: Optional[str] = Query("asc"),
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    q: Optional[str] = Query(None, description="full-text search query"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Contact).filter(models.Contact.owner_id == current_user.id)

    #Filter
    if status:
        query = query.filter(models.Contact.status ==  status)
    if source:
        query = query.filter(models.Contact.source == source)
    if start_date and end_date:
        query = query.filter(models.Contact.created_at.between(start_date, end_date))

    #Global Search
    if q:
        contacts = services.user_service.search_contacts_fuzzy(db, q, skip, limit)
        total = len(contacts)
        return {"total": total, "items": contacts}

    #Sorting
    sort_column = getattr(models.Contact, sort_by, models.Contact.id)
    query = query.order_by(desc(sort_column)) if sort_order == "desc" else query.order_by(asc(sort_column))
    
    total = query.count()
    contacts = query.offset(skip).limit(limit).all()
    return {"total": total, "items": contacts} 


@router.get("/search", response_model=List[schemas.contact.ContactOut])
def search_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    print(db.query(models.Contact).all())
    query = db.query(models.Contact).filter(
        models.Contact.owner_id == current_user.id)
    print(query.all())
    if name:
        query = query.filter(models.Contact.name.ilike(f"%{name}"))
    if email:
        query = query.filter(models.Contact.email.ilike(f"%{email}"))
    return query.offset(skip).limit(limit).all()


@router.put("/{contact_id}", response_model=schemas.ContactOut)
def update_contact(
    contact_id: int,
    updated_contact: schemas.contact.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    contact = db.query(models.Contact).filter_by(
        id=contact_id, owner_id=current_user.id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    for key, value in updated_contact.dict(exclude_unset=True).items():
        setattr(contact, key, value)
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
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
