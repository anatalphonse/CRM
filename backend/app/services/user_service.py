from sqlalchemy.orm import Session
from sqlalchemy import text
from app import models, schemas
from app.core.security import get_password_hashed, verify_password


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hashed(user_in.password)
    db_user = models.user.User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> models.User | None:
    user = db.query(models.user.User).filter(
        models.user.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user(db: Session, user: models.User, update: schemas.UserUpdate) -> models.User:
    if update.name:
        user.name = update.name
    if update.email:
        user.email = update.email
    if update.password:
        user.hashed_password = get_password_hashed(update.password)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: models.User):
    db.delete(user)
    db.commit()


def search_users_fuzzy(db: Session, query: str, skip: int = 0, limit: int = 10):
    sql = text("""
        SELECT * FROM users
        WHERE name ILIKE :q OR email ILIKE :q
        ORDER BY similarity(name, :plain) DESC, similarity(email, :plain) DESC
        LIMIT :limit OFFSET :skip
    """)

    return db.execute(sql, {
        "q": f"%{query}%",
        "plain": query,
        "limit": limit,
        "skip": skip 
    }).fetchall()

def search_contacts_fuzzy(db: Session, query: str, skip: int = 0, limit: int = 10):
    sql = text("""
        SELECT * FROM contacts
        WHERE name ILIKE :q OR email ILIKE :q
        ORDER BY similarity(name, :plain) DESC, similarity(email, :plain) DESC
        LIMIT :limit OFFSET :skip
    """)

    return db.execute(sql, {
        "q": f"%{query}%",
        "plain": query,
        "limit": limit,
        "skip": skip 
    }).fetchall()

def search_leads_fuzzy(db: Session, query: str, skip: int = 0, limit: int = 10):
    sql = text("""
        SELECT * FROM leads
        WHERE name ILIKE :q OR notes ILIKE :q
        ORDER BY similarity(name, :plain) DESC, similarity(notes, :plain) DESC
        LIMIT :limit OFFSET :skip
    """)

    return db.execute(sql, {
        "q": f"%{query}%",
        "plain": query,
        "limit": limit,
        "skip": skip 
    }).fetchall()

