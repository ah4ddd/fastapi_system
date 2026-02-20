from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

#Creates a base class, all database models inherit from it.
Base = declarative_base()

#SQLAlchemy model. It represents the items table.
class ItemDB(Base):
    #actual table name in PostgreSQL.
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) #nullable=False = NOT NULL (required)
    price = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    cost_price = Column(Float, nullable=False)
    supplier_secret = Column(String, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False) # for migration
    created_at = Column(String, nullable=True)  # We'll use proper DateTime later

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
