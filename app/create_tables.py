"""This file is a one-time setup tool.
It creates database tables from your SQLAlchemy models."""
import asyncio # Needed because this file runs an async function manually.
from .database import engine # Imports SQLAlchemy engine.
from .db_models import Base # Imports the Base that holds all models.

"""Take all my models and build their tables in the database
    Base
    ├── ItemDB
    ├── UserDB
    └── Other tables models..."""
async def create_tables():
    """Open a connection to the database
    - Start a transaction
    - Give a connection object called `conn`
    This is a lower-level connection = Engine → Connection → SQL"""
    async with engine.begin() as conn: # conn = live database connection
    # Run this synchronous function safely using this async connection.
        await conn.run_sync(Base.metadata.create_all) # Checks all models and generates SQL table (If table exists: It does nothing)
    print("Tables created successfully!")

"""This file only runs if you execute THIS file directly.
eg: python3 create_tables.py
Then: create_tables() runs and tables get created"""

if __name__ == "__main__":
    asyncio.run(create_tables())

"""
When running:
    python create_tables.py

Internal flow:

- asyncio.run(create_tables()) starts the async event loop.
- engine.begin() requests a connection from the pool.
- A connection is opened and a transaction begins.
- run_sync() bridges async → sync execution.
- Base.metadata.create_all() scans all models.
- SQL is generated for missing tables.
- CREATE TABLE statements are executed.
- Transaction commits.
- Connection returns to the pool.
- Script exits.

Result:
All defined tables are created if they don't already exist.
"""
