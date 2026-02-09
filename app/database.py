from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from .db_models import Base
import os
from dotenv import load_dotenv

# Loads environment variables from .env file.
load_dotenv()

# Get the connection string from environment variables.
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Replace postgresql:// with postgresql+asyncpg:// for async
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

# Creates a factory for database sessions. A session = a conversation with the database.
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency that FastAPI will use to inject database sessions into endpoints.
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
