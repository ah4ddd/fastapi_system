from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from .db_models import Base
import os
from dotenv import load_dotenv

# Loads environment variables from .env file.
load_dotenv()

# Get the connection string from environment variables.
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


# Replace postgresql:// with postgresql+asyncpg:// for async because we're using asyncpg driver (async PostgreSQL driver)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# create_async_engine instead of create_engine
"""Why async? Because we're using async def in FastAPI.
Regular SQLAlchemy would block"""
engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

# Creates a factory for database sessions. A session = a conversation with the database.
"""Creates session factory for async sessions.
use AsyncSession instead of regular Session
- All methods return awaitable objects
- You use await with them
expire_on_commit=False = Don't clear object attributes after commit (keeps them accessible)"""
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency that FastAPI will use to inject database sessions into endpoints.
"""The heart of FastAPI + SQLAlchemy: get_db()
This function is the entire bridge."""
async def get_db():
    """
    Yields a database session for a single request.

    Pulls a connection from the engine's pool, starts a transaction
    context, and ensures the session is closed after the request,
    The context manager handles cleanup."""
    print("Creating database session...")
    async with AsyncSessionLocal() as session:
        # give it to the endpoint
        yield session # When endpoint finishes, session closes automatically
    print("Closing database session...") # proves the session lifecycle.

"""
When an endpoint uses:
    db: AsyncSession = Depends(get_db)

FastAPI handles the session like this:

- A request hits the endpoint.
- FastAPI calls get_db().
- get_db() creates a session and yields it.
- The session is injected into the endpoint.
- The endpoint uses it to talk to the database.
- After the response is returned:
    - get_db() resumes.
    - The async context exits.
    - The session closes.
    - The connection returns to the pool.

Result:
One HTTP request → one DB session.
Each new request gets a fresh session.
"""

