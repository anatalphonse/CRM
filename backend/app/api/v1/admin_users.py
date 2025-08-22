from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_, func
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import TSVECTOR 
from typing import List, Optional
from app import models, schemas, services
from app.core.deps import get_db
from app.core.security import require_roles, require_admin

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin users"]
)


@router.get("", response_model=schemas.user.PaginatedUserOut)
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    email: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("id"),        
    sort_order: Optional[str] = Query("asc"), 
    q: Optional[str] = Query(None, description="search by name or email"),    
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles(["admin"]))
):
    query = db.query(models.User)

    #Optional filter by role
    if role:
        query = query.filter(models.User.role == role)

    # Full text search
    if q:
        users = services.user_service.search_users_fuzzy(db, q, skip, limit)
        total = len(users)
        return {"total": total, "items": users}

    # Sorting
    sort_column = getattr(models.User, sort_by, models.User.id)
    query = query.order_by(desc(sort_column)) if sort_order == "desc" else query.order_by(asc(sort_column))

    total = query.count()
    users = query.offset(skip).limit(limit).all()
    return {"total": total, "items": users}


@router.get("/{user_id}", response_model=schemas.UserSchema)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=schemas.UserSchema)
def update_user(
    user_id: int,
    update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return services.user_service.update_user(db, user, update)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    services.user_service.delete_user(db, user)
    return
