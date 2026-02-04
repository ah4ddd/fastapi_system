from fastapi import APIRouter, HTTPException, status
from app.models import ItemCreate, ItemInPublic, CreateItemResponse, ItemInDB # type: ignore
from app import database as db # type: ignore

#Creates a router object. This will hold all item-related endpoints
#Every route defined on this router gets /items glued in front of it
router = APIRouter(prefix="/items", tags=["items"]) # tags=["items"]? purely for Swagger docs

"""
@router.get does NOT create a server.
It only registers a route on this router object, and replaces app with router.
"""
@router.post("/", response_model=CreateItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate) -> CreateItemResponse:
    """Create a new item"""
    new_item = ItemInDB(
        id=db.get_next_id(),
        name=item.name,
        price=item.price,
        description=item.description,
        cost_price=item.price * 0.6,
        supplier_secret="ACME-42-PRIVATE"
    )

    await db.add_item(new_item)

    return {
        "item": new_item,
        "message": f"Item '{item.name}' created successfully"
    }

@router.get("/", response_model=list[ItemInPublic])
async def get_items():
    """Get all items"""
    return await db.get_all_items()

@router.get("/{item_id}", response_model=ItemInPublic)
async def get_item(item_id: int):
    """Get single item by ID"""
    item = await db.find_item(item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} does not exist"
        )

    return item

@router.put("/{item_id}", response_model=ItemInPublic)
async def update_item(item_id: int, item_update: ItemCreate):
    """Update an existing item"""
    existing_item = await db.find_item(item_id)

    if existing_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} does not exist"
        )

    updated_item = ItemInDB(
        id=existing_item.id,
        name=item_update.name,
        price=item_update.price,
        description=item_update.description,
        cost_price=item_update.price * 0.6,
        supplier_secret=existing_item.supplier_secret
    )

    await db.update_item(item_id, updated_item)
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """Delete an item"""
    deleted = await db.delete_item(item_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} does not exist"
        )
