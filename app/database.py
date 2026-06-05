from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
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
# engine is the database connection manager.
"""
It manages:
connection pool
network communication
database driver
SQL execution

Think of it like this:
FastAPI
   ↓
Session
   ↓
Engine
   ↓
Connection pool
   ↓
Database

Why it's called an engine:
Because it drives communication with the database.
It powers the entire DB layer.
Inside it lives the connection pool.
Example pool:
engine
 └─ pool
     ├─ conn1
     ├─ conn2
     ├─ conn3
     └─ conn4
When a session needs a connection:

session → engine → pool → connection

Why async? Because we're using async def in FastAPI.
Regular SQLAlchemy would block.
"""
engine = create_async_engine(ASYNC_DATABASE_URL, echo=True) # echo=True = Print every SQL query to the terminal

# Creates a factory for database sessions. A session = a conversation with the database.
"""Creates session factory for async sessions.
use AsyncSession instead of regular Session
- All methods return awaitable objects
- You use await with them
expire_on_commit=False = Don't clear object attributes after commit (keeps them accessible)

What a factory means
A factory is simply:
    a function or object that creates other objects`

In this case:
    session factory → creates database sessions

So this line creates a session generator.
Every time you call it:
    AsyncSessionLocal()
You get a new AsyncSession.

Visualizing it:
AsyncSessionLocal (factory)
        │
        ├── session1
        ├── session2
        ├── session3
        └── session4
Each HTTP request gets one.

Why the factory needs the engine?
The factory is configured with:
    engine

So every session created knows:
    which database
    which connection pool
    which driver
Without the engine, sessions wouldn't know how to reach the database.

The class_=AsyncSession
    `class_=AsyncSession`

This tells the factory:
    When you create sessions, make them async sessions

Meaning their methods require:
    await db.execute()
    await db.commit()

Instead of blocking.

expire_on_commit=False:
    Do not wipe object data after commit.

Keep attributes accessible.
Much smoother for APIs.

internally:
    session → borrows connection from engine pool
    session → executes queries
    session → returns connection

You rarely interact with the connection directly.
The session abstracts that layer.
    AsyncSessionLocal creates a new session every time you call it.
"""
AsyncSessionLocal = async_sessionmaker(
    engine, class_= AsyncSession, expire_on_commit=False
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

"""
FULL LIFECYCLE:
Request arrives
      ↓
FastAPI sees Depends(get_db)
      ↓
get_db() starts
      ↓
session created
      ↓
connection borrowed from engine pool
      ↓
yield session
      ↓
endpoint executes queries
      ↓
endpoint returns response
      ↓
get_db resumes
      ↓
session closes
      ↓
connection returned to pool

The whole architecture:
FastAPI endpoint
       ↓
Depends(get_db)
       ↓
AsyncSession
       ↓
Session factory
       ↓
Engine
       ↓
Connection pool
       ↓
PostgreSQL database


Engine: manages database connections and pooling

Factory: object that creates sessions

Session: conversation with the database

Connection: actual network socket to PostgreSQL
"""
