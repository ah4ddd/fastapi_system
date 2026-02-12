from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ItemCreate, ItemInPublic, CreateItemResponse # type: ignore
from app.db_models import ItemDB # type: ignore
from app.database import get_db # type: ignore

router = APIRouter(prefix="/items", tags=["items"])

"""db: AsyncSession = Depends(get_db)
FastAPI calls get_db(), gets a session, injects it as db.
new_item = ItemDB(...)
Creates SQLAlchemy object (Python object, not in DB yet).
db.add(new_item)
Stages object for insertion.
await db.commit()"""
@router.post("/", response_model=CreateItemResponse, status_code=status.HTTP_201_CREATED)
# Injects a database session into endpoint.
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    """Create a new item"""
    new_item = ItemDB(
        name=item.name,
        price=item.price,
        description=item.description,
        cost_price=item.price * 0.6,
        supplier_secret="ACME-42-PRIVATE"
    ) # Create SQLAlchemy object

    db.add(new_item) # Stage for insertion
    await db.commit() # Execute INSERT query
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

@router.get("/", response_model=list[ItemInPublic])
async def get_items(db: AsyncSession = Depends(get_db)):
    """Get all items"""
    result = await db.execute(select(ItemDB)) # SELECT * FROM items
    items = result.scalars().all() # Get all results as Python objects

    return [
        ItemInPublic(
            id=item.id,
            name=item.name,
            price=item.price,
            description=item.description
        )
        for item in items
    ]

@router.get("/{item_id}", response_model=ItemInPublic)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get single item by ID"""
    # SELECT * FROM items WHERE id = ?;
    result = await db.execute(select(ItemDB).where(ItemDB.id == item_id))
    item = result.scalar_one_or_none()

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
    result = await db.execute(select(ItemDB).where(ItemDB.id == item_id))
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} does not exist"
        )

    await db.delete(item)  # Stage for deletion
    await db.commit()  # Execute DELETE query
