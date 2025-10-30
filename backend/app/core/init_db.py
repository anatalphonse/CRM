# app/core/init_db.py
import asyncio
from app.core.database import engine
from app.models.user import Base

async def init_db():
    async with engine.begin() as conn:
        # run synchronous create_all in the async context
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    print("Creating tables...")
    asyncio.run(init_db())
    print("Tables created successfully ✅")
