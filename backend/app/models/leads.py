from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy import DateTime
from sqlalchemy.sql import func


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="new")
    source = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_leads_name_notes_trgm", "name", "notes", postgresql_using="gin"),
    )

    owner = relationship("User", back_populates="leads")