# engine. sessions. dependency injection
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from dotenv import load_dotenv
from typing import Annotated
from fastapi import Depends
from .config import settings # type: ignore

"""
PostrgeSQL NOTES:
*   PostgreSQL Is A Running Program
*   Also PostgreSQL Is A Server:
        When PostgreSQL starts:
            it opens a port.
            Usually: 5432 (listens for SQL requests)
*   Engine is Databse Manager:
    Engine knows:
        database address
        driver
        connection pool
        SQL execution rules
    Its a bridge between Python & PostgreSQL:
            FastAPI
                ↓
            Engine
                ↓
            PostgreSQL
*   CONNECTION. When Python talks to PostgreSQL:
      it opens a network connection.
      Literally. A socket.
      One active communication channel
        Like: Python
                │
                │ TCP connection
                │
                PostgreSQL
*   POOL:
     Engine keeps a pool:
            Pool:
            conn1
            conn2
            conn3
            conn4
    Already open. Already connected. Ready.
        when request arrives:
        Need DB?
        Pool says:
        Take conn2
        Request finishes:
        Return conn2.
        Pool: Reuse. Reuse. Reuse. (Very fast)
*   Session:
     A session is workspace
     Collecting operations then:
      await db.commit()
        SQL travels:
            Session
            ↓
            Connection
            ↓
            PostgreSQL
"""


# Get the connection string from environment variables.
# postgresql://user:pass@localhost:5432/mydb
#  |         │               │      │      │
#  |         │               │      │      └ database
#  └Protocol │               │      └ port
#            │               └host
#            └login credentials
DATABASE_URL = settings.database_url

# Replace postgresql:// with postgresql+asyncpg:// for async
# because we're using asyncpg driver (async PostgreSQL driver)
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

Basically:
    "Hey PostgreSQL, here's my username, password,
    host and port. Let's talk."

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


# Creates a factory for database sessions.
# A session = a conversation with the database.
""" Use AsyncSession instead of regular Session
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
    engine, class_= AsyncSession, expire_on_commit=False, autoflush=False
)


# Dependency that FastAPI will use to inject database sessions into endpoints.
# The heart of FastAPI + SQLAlchemy: get_db()
# This function is the entire bridge.
async def get_db():
    """
    Yields a database session for a single request.

    Pulls a connection from the engine's pool, starts a transaction
    context, and ensures the session is closed after the request,
    The context manager handles cleanup."""
    print("Creating database session...")
    async with AsyncSessionLocal() as session: # create new session
        # give it to the endpoint
        yield session # give it to the endpoint
    # When endpoint finishes, session closes automatically
    print("Closing database session...") # proves the session lifecycle.

# might use this in future
DBDep = Annotated[AsyncSession, Depends(get_db)]

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

FastAPI = one server

PostgreSQL = another server

SQLAlchemy = the translator + traffic manager between them
"""
