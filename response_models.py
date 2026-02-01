from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Input model (what client sends)
class ItemCreate(BaseModel):
    name: str
    price: float
    description: str | None = None

class Item(BaseModel):
    id: int
    name: str
    price: float
    description: str | None = None

# Response model (what you return)
class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    message: str

# Fake database (for now)
fake_db = []
next_id = 1

@app.post("/items", response_model=ItemResponse)
def create_item(item: ItemCreate) -> ItemResponse:
    global next_id

    # Create item with ID
    new_item = Item(
        id=next_id,
        name=item.name,
        price=item.price,
        description=item.description
    )

    fake_db.append(new_item)

    # Prepare response
    response = ItemResponse(
        id=next_id,
        name=item.name,
        price=item.price,
        message=f"Item '{item.name}' created successfully"
    )

    next_id += 1
    return response

@app.get("/items", response_model=list[Item])
def get_items() -> list[Item]:
    return fake_db

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    for item in fake_db:
        if item.id == item_id:
            return item

    raise HTTPException(status_code=404, detail="Item not found")
