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

# Replace postgresql:// with postgresql+asyncpg:// for async because we're using async driver.
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
"""Why async? Because we're using async def in FastAPI.
Regular SQLAlchemy would block"""
engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

# Creates a factory for database sessions. A session = a conversation with the database.
"""Creates session factory for async sessions.
expire_on_commit=False = Don't clear object attributes after commit (keeps them accessible)"""
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency that FastAPI will use to inject database sessions into endpoints.
async def get_db():
    # Creates a session
    async with AsyncSessionLocal() as session:
        # give it to the endpoint
        yield session # When endpoint finishes, session closes automatically
