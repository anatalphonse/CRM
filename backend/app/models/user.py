from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from app.core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean
from sqlalchemy.sql import func
import enum, uuid


class UserRole(enum.Enum):
    admin = "admin"
    manager = "manager"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, unique=True, nullable=True, default=lambda: str(uuid.uuid4()))
    password_reset_token = Column(String, nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_users_name_email_trgm", "name", "email", postgresql_using = "gin"),
    )

    contacts = relationship("Contact", back_populates="owner", cascade="all, delete")
    leads = relationship("Lead", back_populates="owner", cascade="all, delete")
    tasks = relationship("Task", back_populates="owner", cascade="all, delete")