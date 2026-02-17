from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ItemCreate, ItemInPublic, CreateItemResponse # type: ignore
from app.db_models import ItemDB # type: ignore
from app.database import get_db # type: ignore

# Rule: Anything that performs I/O (talks to the DB over network) needs await.

"""
APIRouter Configuration
prefix: Auto-prepends "/items" to all routes in this file (e.g., /items/{id}).
        Prevents repetitive path typing.
tags: Groups these routes under an "items" header in the /docs UI.
        Purely for organizing the Swagger documentation."""
router = APIRouter(prefix="/items", tags=["items"])

"""db: AsyncSession = Depends(get_db)
FastAPI calls get_db(), gets a session, injects it as db.
new_item = ItemDB(...)
Creates SQLAlchemy object (Python object, not in DB yet).
db.add(new_item)
Stages object for insertion.
await db.commit()"""
@router.post("/", response_model=CreateItemResponse, status_code=status.HTTP_201_CREATED)
# Injects a database session into endpoint, calls get_db(), gets the session, injects it as 'db', ItemCreate = Pydantic model (API layer)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    """Create new item with SQLAlchemy model (DB layer) = ItemDB
    This represents:
    Database table, Columns, Rows
    This is what actually maps to PostgreSQL"""
    new_item = ItemDB(
        name=item.name,
        price=item.price,
        description=item.description,
        cost_price=item.price * 0.6,
        supplier_secret="ACME-42-PRIVATE"
    ) # Create SQLAlchemy object. Pydantic → SQLAlchemy object

    db.add(new_item) # Stage for insertion (Track this object. I plan to insert it)
    # db.commit() is an async function. It returns a coroutine, must await it to actually execute.
    await db.commit() # Execute INSERT query (Take everything I staged and make it permanent in the database)
    await db.refresh(new_item) # Reloads the object from database to get the auto-generated id.

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
    # SELECT * FROM items WHERE id = ?; where() adds a WHERE clause to the SELECT
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
    result = await db.execute(select(ItemDB).where(ItemDB.id == item_id))
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

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an item"""
    # Find row
    result = await db.execute(select(ItemDB).where(ItemDB.id == item_id))
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} does not exist"
        )

    await db.delete(item)  # Stage for deletion
    await db.commit()  # Execute DELETE query

"""
Let's simulate it mentally

Imagine FastAPI doing this:

Start request

Call get_db()
 → creates session
 → enters async with
 → hits yield
 → pauses here

Run your endpoint with that session

Endpoint finishes

Resume get_db()
 → exit async with
 → session closes

End request


This is dependency lifecycle management.
"""
