from pydantic import BaseModel, Field

# What the CLIENT sends (input)
class ItemCreate(BaseModel):
    name: str = Field(min_length=3)
    price: float = Field(gt=0)
    description: str | None = Field(default=None, max_length=200)
    stock_quantity: int = 0

# What lives in DATABASE (internal)
class ItemInDB(ItemCreate):
    id: int
    cost_price: float
    supplier_secret: str

# What the CLIENT receives (output)
class ItemInPublic(BaseModel):
    id: int
    name: str
    price: float
    description: str | None = None

# Wrapper for POST response
class CreateItemResponse(BaseModel):
    item: ItemInPublic
    message: str
