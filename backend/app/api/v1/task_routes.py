from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession as Session
from app.core.deps import get_db
from app import models, schemas, services
from app.core.security import get_current_user
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func, or_, desc, asc

router = APIRouter()


@router.post("", response_model=schemas.task.TaskOut)
def create_task(task: schemas.task.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = models.Task(**task.dict(), owner_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
