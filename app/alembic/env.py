"""
This file runs only during Alembic migrations,
not as part of the application runtime.

It acts as the bridge between:
Alembic ↔ SQLAlchemy ↔ Database

Coordinates:
- Alembic config (alembic.ini)
- Environment variables (.env)
- Models (Base.metadata)
- Database engine
- Migration scripts

Enables Alembic to:
- Detect schema changes
- Generate SQL
- Apply migrations safely
"""

"""
Connection Layer:

DATABASE_URL
    ↓
Config object
    ↓
Engine
    ↓
Connection

Alembic coordinates runtime config + DB connection + metadata
   comparison through a context-managed migration environment
"""
# alembic.ini → parsed → config object → used to build engine
# env.py → Alembic ↔ SQLAlchemy ↔ Database
# versions/ = migration history, Each file = one schema change
# script.py,mako = Template file

import asyncio # because using async migrations
import os # to read environment variables
from logging.config import fileConfig # sets up logging from alembic.ini

# SQLAlchemy → defines models, talks to DB, runs queries
from sqlalchemy import pool # controls how DB connections are handled
from sqlalchemy.engine import Connection # type hint for DB connection
from sqlalchemy.ext.asyncio import async_engine_from_config # creates an async SQLAlchemy engine using Alembic config

# Alembic → manages schema changes over time
"""
`context`is Alembic's central control object.

`context` manages configuration, migration execution,
runtime mode (online/offline), and transaction handling.
All migration operations pass through it, manages the migration lifecycle.
"""
from alembic import context # context = Alembic runtime brain
# This lets Alembic read your .env file because Alembic runs outside FastAPI
from dotenv import load_dotenv

# Load .env file so we can get DATABASE_URL string
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
# Crash if missing
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# This is the Alembic Config object, gives Alembic’s loaded configuration.
# represents the parsed contents of alembic.ini.
"""
This grabs Alembic's internal configuration object.
This object reads: alembic.ini, runtime settings and stores in in memory
as `config`. (can modify and read settings through it)
"""
config = context.config

# Override the database URL for Alembic using the value from .env.
# Alembic normally reads this from alembic.ini, but we inject it here,
# so migrations use the same async connection settings as the app.
"""
Reads DATABASE_URL from the environment, converts it to the async
driver format, and sets it in Alembic's config so it knows which
database to connect to when running migrations.
"""
config.set_main_option( # modifies the config object in memory.
    "sqlalchemy.url",
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
) # Equivalent of doing: sqlalchemy.url = new_url

# This loads logging settings from alembic.ini.
# Interpret the config file for Python logging (does NOT create files.)
# This sets: log level, formatting, output behavior
"""
It configures Python's logging system.
Not DB.
Not migrations.
Just logs.
"""
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is critical. Alembic needs to see models to know
#   what the schema should look like.
from db_models import Base # type: ignore

"""
Tells Alembic: This is what my database SHOULD look like. Compare it to what it ACTUALLY looks like and generate the difference
Alembic compares:
metadata (models) VS actual DB schema, to detect differences.
"""
# Contains: table, names, columns, types, constraints, indexes, primary keys forgein key
target_metadata = Base.metadata

"""
These functions return nothing because their purpose is side effects.

They:
- Configure Alembic
- Start a transaction
- Execute migration SQL

No data is returned.
They directly modify the database state.
"""

# This is for a rare case.
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This is for generating SQL scripts without connecting to DB.
    Useful for reviewing what will run before running it."""

    # This reads from the config object, so this retrieves: DATABASE_URL
    url = config.get_main_option("sqlalchemy.url")
    # Sets up migration environment using just the URL.
    context.configure(
        # The database location, but in offline mode: It DOES NOT CONNECT,
        # just uses URL to know DB type.
        url=url,
        # Gives Alembic model schema (what DB should look like)
        target_metadata=target_metadata,
        # When generating SQL, put value directly into SQL string
        literal_binds=True,
        # Controls SQL formatting style.
        # This depends on DB dialect (Postgres, MySQL, etc.)
        dialect_opts={"paramstyle": "named"},
    )
    # starts transaction and executes migration SQL
    with context.begin_transaction():
        context.run_migrations()

# The actual migration executor
"""
This time, it has:
real DB connection
real schema
model schema
Now it can compare both.
"""
# connection: Connection is `type hint`
# The thing pass into this function must be a SQLAlchemy Connection object.
# connection = sync DB connection
def do_run_migrations(connection: Connection) -> None:
    # gives Alembic real Db connection and model schema (Now Alembic is ONLINE)
    context.configure(connection=connection, target_metadata=target_metadata)
    # Starts a DB transaction, Equivalent SQL: BEGIN;
    with context.begin_transaction():
        # loads migration from `version/` and executes: upgrade()
        # Runs migration scripts from the versions/ directory.
        # Each migration file contains an upgrade() function
        # with operations like:
        #     op.add_column(...)
        #
        # Alembic translates these operations into SQL, e.g.:
        #     ALTER TABLE items ADD COLUMN stock_quantity INTEGER;

        context.run_migrations()


# Async migration runner. Needed because project uses async SQLAlchemy.
async def run_async_migrations() -> None:
    """builds an async engine using config settings, reads from `config`,
       and finds sqlaclchemy.url and builds and engine from it"""
    # Reads: URL, pool settings, dialect from config
    # Creates async engine using Alembic config
    connectable = async_engine_from_config(
        # Give the entire [alembic] section from alembic.ini
        config.get_section(config.config_ini_section, {}),
        # Only read keys starting with `sqlalchemy.`, extracts `sqlalchemy.url`
        prefix="sqlalchemy.",
        # Create connection. Use it. Destroy it.
        poolclass=pool.NullPool,  # Don't pool connections during migrations
    )

    # opens DB connection, Runs migration logic using it
    # real DB connection assingns it to: `connection`
    async with connectable.connect() as connection: # AsyncConnection object
        # Alembic gives this function a REAL live DB connection, it Does:
        # Take async connection
        # ↓
        # Convert to sync connection
        # ↓
        # Call:
        # do_run_migrations(sync_connection)
      await connection.run_sync(do_run_migrations)
    # Closes engine cleanly: Closes connections. Releases resources.
    await connectable.dispose()

# Online mode wrapper. Starts async event loop to run migrations.
def run_migrations_online() -> None:
    # Starts async event loop to run migrations.
    asyncio.run(run_async_migrations())

"""
Determine how Alembic was invoked.

context.is_offline_mode() checks the execution mode:

Online mode:
    alembic upgrade head
    → Connects to the database and applies migrations directly.

Offline mode:
    alembic upgrade head --sql
    → Generates SQL statements without connecting to the database.

Based on the mode, the appropriate migration function is executed.
"""
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

"""
Alembic Migration Lifecycle (Async Setup)

run `alembic upgrade head`
        ↓
Alembic starts
        ↓
Reads alembic.ini
        ↓
Loads env.py
        ↓
env.py loads .env
        ↓
Reads DATABASE_URL
        ↓
Creates async engine
        ↓
run_migrations_online()
        ↓
Creates DB connection
        ↓
connection.run_sync(do_run_migrations)
        ↓
context.configure(...)
        ↓
BEGIN TRANSACTION
        ↓
Loads Base.metadata (all models)
        ↓
Compares:
    DB schema  ↔  Model schema
        ↓
context.run_migrations()
        ↓
Migration operations (op.*)
        ↓
Translated to SQL:
    CREATE TABLE / ALTER TABLE ...
        ↓
COMMIT
        ↓
Connection closes
        ↓
Engine disposed
        ↓
Done
"""
