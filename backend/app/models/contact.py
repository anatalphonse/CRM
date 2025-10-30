from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, ForeignKey, Index
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy import DateTime

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    source = Column(String)
    status = Column(String)
    notes = Column(String)
    company = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Use gin_trgm_ops for text columns so GIN trigram works
    __table_args__ = (
        Index(
            "idx_contacts_name_email_trgm",
            "name",
            "email",
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops", "email": "gin_trgm_ops"},
        ),
    )

    owner = relationship("User", back_populates="contacts")
