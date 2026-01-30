from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel #data validation and parsing library for Python

#App instance
#This object represents my entire service
app = FastAPI()

items_db = []
item_id_counter = 1

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
@app.get("/item/{item_id}")
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

class ItemInDB(ItemCreate):
    id: int
    #internal
    cost_price : float
    supplier_secret: str

class ItemInPublic(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None

# response_model = An output filter + validator that runs AFTER your function finishes
@app.post("/create_items", response_model=ItemInPublic)
def create_item(item: ItemCreate): #validates it as ItemCreate
    global item_id_counter #modify global counter

    #validated object with server-assinged ID
    new_item = ItemInDB(
        id=item_id_counter,
        name=item.name,
        price=item.price,
        description=item.description,
        cost_price=item.price* 0.6,
        supplier_secret="ACME-42-PRIVATE"
    )

    #stores in memory till server is alive
    items_db.append(new_item)
    item_id_counter += 1

    return new_item #returns json formatted string converted from stored object


#Response is a list, and the elements inside that list follow the ItemInDB schema
@app.get("/items", response_model=list[ItemInPublic])
def get_items():
    '''
serialized json conversion pipeline:
ItemInDB object
→ item.dict()
→ Python dict
→ JSON string
→ HTTP response
'''
    return items_db
