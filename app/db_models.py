from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base

# SQLAlchemy database models

# Creates a base class,
# All database models inherit from it.
# It tracks all table classes so SQLAlchemy knows what exists.
Base = declarative_base()

#SQLAlchemy model. It represents the items table.
# ItemDB is the Python class that represents the "items" table,
# and is used by SQLAlchemy to perform database operations.
class ItemDB(Base):
    #actual table name in PostgreSQL.
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True) # SQL INTEGER PRIMARY KEY
    name = Column(String, nullable=False) # nullable=False = NOT NULL (required)
    price = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    cost_price = Column(Float, nullable=False)
    supplier_secret = Column(String, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)

class WeatherDB(Base):
    # create a weather_data table in PostgreSQL
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    humidity = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

class GitHubRepoDB(Base):
    __tablename__ = "github_repos"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, index=True)
    repo_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    stars = Column(Integer, default=0)
    language = Column(String)
    url = Column(String)
    updated_at = Column(String)
    fetched_at = Column(String, nullable=False)  # When we fetched this data

class CryptoPriceDB(Base):
    __tablename__ = "crypto_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    price_usd = Column(Float, nullable=False)
    change_24h = Column(Float, default=0)
    timestamp = Column(String, nullable=False)

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # email unique: Can't have two users with same email
    # email index: Fast lookups when logging
    email = Column(String, unique=True, nullable=False, index=True)
    # hashed_password: NEVER store plain passwords
    hashed_password = Column(String, nullable=False)
    created_at = Column(String, nullable=False)


"""
ALEMBIC :

Generate Initial Migration: `alembic revision --autogenerate -m "commit message"`
    revision = Create a new migration file
    --autogenerate = Compare your models to the database and auto-generate the SQL
    -m "commit message" = Message (like a git commit message)

Apply the Migration : `alembic upgrade head`
    Apply all migrations up to the latest one. head = the most recent version.
    runs : ALTER TABLE items ADD COLUMN stock_quantity INTEGER NOT NULL DEFAULT 0;

The Migration Chain (How Versions Connect):
None
  ↓
a1b2c3d4e5f6  "create items table"
  ↓
b7c8d9e0f1a2  "add stock_quantity to items"
  ↓
c3d4e5f6a7b8  "add users table"          ← future
  ↓
HEAD (latest)
"""

"""
Alembic Migration Commands
---------------------------

Generate Initial Migration:
    alembic revision --autogenerate -m "commit message"

Apply all migrations:
    alembic upgrade head

Apply one migration forward:
    alembic upgrade +1

Revert one migration:
    alembic downgrade -1

Revert to a specific version:
    alembic downgrade <revision_id>

Revert all migrations:
    alembic downgrade base

Check current DB revision:
    alembic current

View migration history:
    alembic history
"""
