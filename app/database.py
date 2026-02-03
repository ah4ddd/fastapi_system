from .models import ItemInDB

# In-memory database
items_db: list[ItemInDB] = []
item_id_counter = 1

def get_next_id() -> int:
    """Get next available ID and increment counter"""
    global item_id_counter
    current_id = item_id_counter
    item_id_counter += 1
    return current_id

async def find_item(item_id: int) -> ItemInDB | None:
    """Search items_db for item with matching ID"""
    # Using async even though it's in-memory to prepare for real DB
    for item in items_db:
        if item.id == item_id:
            return item
    return None

async def get_all_items() -> list[ItemInDB]:
    """Return all items from database"""
    return items_db

async def add_item(item: ItemInDB) -> ItemInDB:
    """Add item to database"""
    items_db.append(item)
    return item

async def update_item(item_id: int, updated_item: ItemInDB) -> ItemInDB:
    """Update existing item in database"""
    for index, item in enumerate(items_db):
        if item.id == item_id:
            items_db[index] = updated_item
            return updated_item
    raise ValueError(f"Item {item_id} not found")

async def delete_item(item_id: int) -> bool:
    """Delete item from database. Returns True if deleted."""
    item = await find_item(item_id)
    if item:
        items_db.remove(item)
        return True
    return False
