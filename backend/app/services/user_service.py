from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.future import select
from sqlalchemy import desc, asc, or_, func
from app import models, schemas
from app.core.security import get_password_hashed, verify_password
from typing import List, Optional
from app.models.user import User


async def create_user(db: AsyncSession, user_in: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hashed(user_in.password)
    db_user = models.user.User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> models.User | None:
    result = await db.execute(
        select(models.user.User).where(models.user.User.email == email)
    )
    user = result.scalars().first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def update_user(db: AsyncSession, user: models.User, update: schemas.UserUpdate) -> models.User:
    if update.name:
        user.name = update.name
    if update.email:
        user.email = update.email
    if update.password:
        user.hashed_password = get_password_hashed(update.password)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: models.User):
    await db.delete(user)
    await db.commit()


async def search_users_fuzzy(
        db: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 10,
        role: Optional[str] = None,  # Add role parameter
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc"
) -> List:

    # Sanitize sort order
    order = "DESC" if sort_order and sort_order.lower() == "desc" else "ASC"

    # Allow sorting by only certain columns for security
    allowed_sort_columns = ["name", "email", "created_at", "id", "role"]
    sort_column = sort_by if sort_by in allowed_sort_columns else "id"

    # Build WHERE conditions
    where_conditions = ["(name ILIKE :q OR email ILIKE :q)"]
    params = {
        "q": f"%{query}%",
        "plain": query,
        "limit": limit,
        "skip": skip
    }

    # Add role filter if provided
    if role:
        where_conditions.append("role = :role")
        params["role"] = role

    sql = text(f"""
        SELECT * FROM users
        WHERE {' AND '.join(where_conditions)}
        ORDER BY {sort_column} {order}, similarity(name, :plain) DESC, similarity(email, :plain) DESC
        LIMIT :limit OFFSET :skip
    """)

    # Execute with await
    result = await db.execute(sql, params)
    return result.fetchall()

# Add helper function for getting total count


async def get_total_count(
        db: AsyncSession,
        query: str,
        role: Optional[str] = None
) -> int:

    where_conditions = ["(name ILIKE :q OR email ILIKE :q)"]
    params = {
        "q": f"%{query}%"
    }

    if role:
        where_conditions.append("role = :role")
        params["role"] = role

    sql = text(f"""
        SELECT COUNT(*) FROM users
        WHERE {' AND '.join(where_conditions)}
    """)

    result = await db.execute(sql, params)
    return result.scalar()

# services/user_service.py


async def get_users_paginated(
    db: AsyncSession,
    skip: int,
    limit: int,
    role: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    search_query: Optional[str] = None
) -> List[User]:
    """Unified method for getting paginated users with optional search and filters."""

    if search_query:
        # Use your existing fuzzy search logic
        return await search_users_fuzzy(
            db, search_query, skip, limit, role, sort_by, sort_order
        )

    # Regular query
    query = select(models.User)

    if role:
        query = query.where(models.User.role == role)

    # Safe sorting with predefined mapping
    sort_mapping = {
        "id": models.User.id,
        "name": models.User.name,
        "email": models.User.email,
        "created_at": models.User.created_at,
        "role": models.User.role
    }

    sort_column = sort_mapping.get(sort_by, models.User.id)
    query = query.order_by(
        desc(sort_column) if sort_order == "desc" else asc(sort_column))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_total_count_filtered(
    db: AsyncSession,
    role: Optional[str] = None,
    search_query: Optional[str] = None
) -> int:
    """Get total count with consistent filtering logic."""

    if search_query:
        # Use your existing search count logic
        return await get_total_count(db, search_query, role)

    query = select(func.count(models.User.id))

    if role:
        query = query.where(models.User.role == role)

    result = await db.execute(query)
    return result.scalar()


async def search_contacts_fuzzy(db: AsyncSession, query: str, skip: int = 0, limit: int = 10):
    sql = text("""
        SELECT * FROM contacts
        WHERE name ILIKE :q OR email ILIKE :q
        ORDER BY similarity(name, :plain) DESC, similarity(email, :plain) DESC
        LIMIT :limit OFFSET :skip
    """)

    # Bind parameters
    params = {
        "q": f"%{query}%",
        "plain": query,
        "limit": limit,
        "skip": skip
    }

    # Execute with await
    result = await db.execute(sql, params)
    return result.fetchall()


async def search_leads_fuzzy(db: AsyncSession, query: str, skip: int = 0, limit: int = 10):
    sql = text("""
        SELECT * FROM leads
        WHERE name ILIKE :q OR notes ILIKE :q
        ORDER BY similarity(name, :plain) DESC, similarity(notes, :plain) DESC
        LIMIT :limit OFFSET :skip
    """)

    # Bind parameters
    params = {
        "q": f"%{query}%",
        "plain": query,
        "limit": limit,
        "skip": skip
    }

    # Execute with await
    result = await db.execute(sql, params)
    return result.fetchall()
