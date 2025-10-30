from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, asc, or_, func
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import TSVECTOR
from typing import List, Optional
from sqlalchemy.future import select
from app import models, schemas, services
from app.core.deps import get_db
from app.core.security import require_roles
import asyncio
import logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=schemas.user.PaginatedUserOut)
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    role: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("id"),
    sort_order: Optional[str] = Query("asc"),
    q: Optional[str] = Query(None, description="search by name or email"),
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(require_roles(["admin"]))
):
    # Validate sort parameters
    allowed_sort_fields = {"id", "name", "email", "created_at", "role"}
    if sort_by not in allowed_sort_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    
    try:
        # Run both queries concurrently using asyncio.gather
        users_task, total_task = await asyncio.gather(
            services.user_service.get_users_paginated(
                db, skip, limit, role, sort_by, sort_order, q
            ),
            services.user_service.get_total_count_filtered(
                db, role, q
            ),
            return_exceptions=True
        )
        
        # Handle any exceptions
        if isinstance(users_task, Exception):
            raise users_task
        if isinstance(total_task, Exception):
            raise total_task
            
        return {"total": total_task, "items": users_task}
        
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



@router.get("/{user_id}", response_model=schemas.UserSchema)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(require_roles(["admin"]))
):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=schemas.UserSchema)
async def update_user(
    user_id: int,
    update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(require_roles(["admin"]))
):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    result = await services.user_service.update_user(db, user, update)
    return result


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(require_roles(["admin"]))
):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    await services.user_service.delete_user(db, user)
    return
