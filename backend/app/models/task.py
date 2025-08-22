from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, ForeignKey, Index, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    head = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="todo")
    team_id = Column(Integer, nullable=False)
    assigned_to = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    reporter = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index(
            "idx_tasks_head_trgm",
            "head",
            postgresql_using="gin",
            postgresql_ops={"head": "gin_trgm_ops"},
        ),
    )

    owner = relationship("User", back_populates="tasks")
