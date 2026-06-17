# APIRouter = route container, it stores endpoint
# HTTPException = Returns errors to clients
# status = collection of HTTP status codes
# Depends = dependency injection
from fastapi import APIRouter, HTTPException, status, Depends
# AsyncSession is the asynchronous database session object
# used to talk to the database without blocking the server.
from sqlalchemy.ext.asyncio import AsyncSession # .ext means inside extension
# translator between Python objects and SQL queries.
# construct SQL queries using Python objects instead of raw SQL strings.
from sqlalchemy import select
"""
The pipeline becomes:

request arrives
      ↓
APIRouter matches route
      ↓
endpoint function runs
      ↓
Depends(get_db) creates DB session
      ↓
select() builds SQL query
      ↓
AsyncSession executes query
      ↓
database returns row
      ↓
response returned

Every import you asked about sits in this pipeline.
"""

from app.models import ItemCreate, ItemInPublic, CreateItemResponse # type: ignore
# ItemDB is the ORM model that represents a database table.
from app.db_models import ItemDB # type: ignore
from app.database import get_db # type: ignore

from typing import Annotated

# Rule: Anything that performs I/O (talks to the DB over network) needs await.
"""
APIRouter Configuration
prefix: Auto-prepends "/items" to all routes in this file (e.g., /items/{id}).
        Prevents repetitive path typing.
tags: Groups these routes under an "items" header in the /docs UI.
        Purely for organizing the Swagger documentation."""
# Think of a router like a container that collects endpoints.
router = APIRouter(prefix="/items", tags=["items"])

"""db: AsyncSession = Depends(get_db)
FastAPI calls get_db(), gets a session, injects it as db.
new_item = ItemDB(...)
Creates SQLAlchemy object (Python object, not in DB yet).
db.add(new_item)
Stages object for insertion.
await db.commit()"""
@router.post("/", response_model=CreateItemResponse, status_code=status.HTTP_201_CREATED)
# Injects a database session into endpoint, calls get_db(),
# gets the session, injects it as 'db', ItemCreate = Pydantic model (API layer)
async def create_item(
    item: ItemCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
    ):
    #Create new item with SQLAlchemy model (DB layer) = ItemDB
    # This represents:
    # Database table, Columns, Rows
    # This is what actually maps to PostgreSQL
    # ItemDB ORM, its job is: Map a Python class to a database table
    new_item = ItemDB(
        name=item.name,
        price=item.price,
        description=item.description,
        cost_price=item.price * 0.6,
        supplier_secret="ACME-42-PRIVATE",
        stock_quantity = item.stock_quantity
    ) # Create SQLAlchemy object. Pydantic → SQLAlchemy object

    # stages the object in the session. Nothing written to DB yet
    db.add(new_item)
    # db.commit() is an async function.
    # It returns a coroutine, must await it to actually execute.
    await db.commit() # sends INSERT to PostgreSQL, transaction completes
    # Syncs the Python object with the database row.
    await db.refresh(new_item)

    return {
        "item": ItemInPublic(
            id=new_item.id,
            name=new_item.name,
            price=new_item.price,
            description=new_item.description
        ),
        "message": f"Item '{item.name}' created successfully"
    }


"""
How an endpoint actually works (step-by-step):
1. HTTP request arrives.
2. FastAPI detects `Depends(get_db)`.
3. `get_db()` is called.
4. A database session is created.
5. The session is injected into `get_products`.
6. The query executes.
7. A response is returned to the client.
8. FastAPI resumes `get_db()`.
9. `db.close()` runs.
10. The connection is returned to the pool.
You never manually manage sessions inside routes.
That's the whole point.
"""
@router.get("/", response_model=list[ItemInPublic])
async def get_items(db: AsyncSession = Depends(get_db)):
    """
    - execute() runs the SQL query which fetches data,
    and brings results from the database into memory
    - It stores them inside a result container
    - .scalars() extracts the ORM objects from each row
    - .all() turns them into a Python list
    - That list is now usable in your endpoint"""
    result = await db.execute(select(ItemDB)) # SELECT * FROM items
    items = result.scalars().all() # Get all results as Python objects into a list

    return [
        ItemInPublic(
            id=item.id,
            name=item.name,
            price=item.price,
            description=item.description
        )
        for item in items
    ]

"""
Depends(). Full Dependency Flow:
Request arrives
    ↓
FastAPI sees: db = Depends(get_db)
    ↓
FastAPI calls: get_db()
    ↓
get_db() creates AsyncSession
    ↓
FastAPI injects session as 'db' parameter
    ↓
Your endpoint uses 'db'
    ↓
Endpoint finishes
    ↓
get_db's 'async with' closes session
    ↓
Response sent

Every request gets its own session. Session closes automatically.
"""


@router.get("/{item_id}", response_model=ItemInPublic)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get single item by ID"""
    # SELECT * FROM items WHERE id = ?: where() adds a WHERE clause to the SELECT
    result = await db.execute(select(ItemDB).where(ItemDB.id == item_id))
    item = result.scalar_one_or_none() # Give me exactly one object if it exists. If nothing is found, return None

    # If DB didn’t find that ID send 404.
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} does not exist"
        )

    return ItemInPublic(
        id=item.id,
        name=item.name,
        price=item.price,
        description=item.description
    )
"""
db
│
├── engine reference
├── connection (open, active)
├── transaction state
├── identity map (object tracker)
└── pending changes

db (AsyncSession)
│
├── connection → PostgreSQL
├── pending_inserts → [new_item]
├── loaded_objects → {id: object}
├── dirty_objects → modified rows
└── transaction_state → active

Engine
 └── Pool
      ├── Conn1
      ├── Conn2
      ├── Conn3
      └── Conn4 (open → use → return → use → return → use → return)
"""
@router.put("/{item_id}", response_model=ItemInPublic)
async def update_item(item_id: int, item_update: ItemCreate, db: AsyncSession = Depends(get_db)):
    """Update an existing item"""
    # fetching the row from the database.
    # The AsyncSession sends that SQL to PostgreSQL
    # The database returns rows.
    # But SQLAlchemy wraps the result in a result object
    # SELECT * FROM items WHERE id = ?
    result = await db.execute(select(ItemDB).where(ItemDB.id == item_id))
    # The query result may contain: 0 rows, 1 row, many rows
    # scalar_one_or_none() means:
        # if 0 rows → return None
        # if 1 row → return that object
        # if >1 rows → throw error
    # In our case the query filters by primary key id, so only one row can exist
    existing_item = result.scalar_one_or_none()

    if existing_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} does not exist"
        )
    # Change attribute
    existing_item.name = item_update.name
    existing_item.price = item_update.price
    existing_item.description = item_update.description
    existing_item.cost_price = item_update.price * 0.6
    # Execute UPDATE query
    #SQLAlchemy detects changes and executes:
    await db.commit() # UPDATE items SET name = ?, price = ?, cost_price = ? WHERE id = ?;
    await db.refresh(existing_item)

    return ItemInPublic(
        id=existing_item.id,
        name=existing_item.name,
        price=existing_item.price,
        description=existing_item.description
    )
"""
So the lifecycle for UPDATE:
Client sends PUT /items/5
        ↓
Query database
        ↓
Load ItemDB object
        ↓
Modify attributes
        ↓
SQLAlchemy marks object dirty
        ↓
commit()
        ↓
ORM generates UPDATE SQL
        ↓
Database updates row
"""


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete an item:
    """

    # SELECT *
    # FROM items
    # WHERE id = 5;
    result = await db.execute(select(ItemDB).where(ItemDB.id == item_id))
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} does not exist"
        )

    await db.delete(item)  # item cheduled for deletion (session memory)
    await db.commit()  # Execute DELETE query.
"""
Lifecycle for DELETE
Client sends DELETE /items/5
        ↓
Query database
        ↓
Load ItemDB object
        ↓
db.delete(item)
        ↓
Session marks object for deletion
        ↓
commit()
        ↓
ORM generates DELETE SQL
        ↓
Database removes row
"""


"""
ItemDB - SQLAlchemy ORM Model for the `items` Table
===================================================

ItemDB is the database-layer representation of an item. It maps a Python class
to the `items` table in PostgreSQL using SQLAlchemy's ORM system.

This model defines the table schema and is the object used by SQLAlchemy
sessions to perform CRUD operations against the database.

────────────────────────────────────────────────────
Role in the System Architecture
────────────────────────────────────────────────────

Client Request
      ↓
FastAPI Endpoint
      ↓
Pydantic Models (validation / API schema)
      ↓
ItemDB (ORM model)
      ↓
SQLAlchemy Session
      ↓
Database Engine
      ↓
PostgreSQL Table: `items`

ItemDB acts as the bridge between Python objects and database rows.

────────────────────────────────────────────────────
What ItemDB Represents
────────────────────────────────────────────────────

A single instance of ItemDB corresponds to one row in the database.

Example database row:

    id = 5
    name = "Phone"
    price = 300

Becomes the Python object:

    ItemDB(id=5, name="Phone", price=300)

This allows application code to work with Python objects instead of raw SQL rows.

────────────────────────────────────────────────────
How It Is Used in CRUD Operations
────────────────────────────────────────────────────

CREATE
    new_item = ItemDB(...)
    db.add(new_item)
    await db.commit()

READ
    result = await db.execute(select(ItemDB))
    items = result.scalars().all()

UPDATE
    existing_item.name = "New Name"
    await db.commit()

DELETE
    await db.delete(existing_item)
    await db.commit()

SQLAlchemy tracks changes to ItemDB objects and automatically generates the
appropriate SQL statements when `commit()` is called.

────────────────────────────────────────────────────
Important Notes
────────────────────────────────────────────────────

• ItemDB is NOT used for API validation or responses.
  Those responsibilities belong to Pydantic models such as:
      - ItemCreate
      - ItemInPublic

• ItemDB is strictly part of the database layer.

• Alembic migrations read this model to generate database schema changes.

────────────────────────────────────────────────────
Mental Model
────────────────────────────────────────────────────

ItemDB = Python representation of a database row.

It defines:
    - table name
    - columns
    - data types
    - constraints

And enables the ORM to translate Python object operations into SQL queries.
"""
