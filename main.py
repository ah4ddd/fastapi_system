from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel #data validation and parsing library for Python

#App instance
#This object represents my entire service
app = FastAPI()

#creating endpoints with decorators
@app.get("/")
def read_root():
    return {"message": "System is alive"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/mission")
def mission():
    return {"mission":"Learn Fastapi and build cool shit"}

#path parameter
@app.get("/items/{item_id}")
#automatic validation
def read_item(item_id: int): #type hint, validates it's an integar
    return {"item_id": item_id, "name": f"Item {item_id}"}

#query parameter (anything after '?' in URL)
@app.get("/search")
def search_item(q: Optional[str] = None, limit: int = 10):
    return { # on web = ?key=value&key=value&key=value
        "query": q,
        "limit": limit,
        "message": f"Searching for '{q} with {limit}"}

'''Defining a pydantic model (data schema + validation),
    'class Item' follows pydantic rules'''
class ItemCreate(BaseModel): # base class that all Pydantic models inherit from
    #custom data structure (dict-json format)
    name: str
    price: float
    description: Optional[str] = None

#input request model
@app.post("/create_items")
def create_item(item: ItemCreate): #validate client data against 'Item'
    return {"item": item}


