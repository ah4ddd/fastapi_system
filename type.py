from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class ItemCreate(BaseModel):
    name: str = Field(min_length=3)
    price: float = Field(gt=0)
    description: str | None = Field(default=None, max_length=200)

@app.post("/items")
def create_item(item: ItemCreate):
    return item
