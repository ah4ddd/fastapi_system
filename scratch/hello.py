from fastapi import FastAPI, Query, Path
from enum import Enum
from pydantic import BaseModel, AfterValidator
from typing import Annotated
import random


app = FastAPI()

@app.get("/") # path operation decorator
async def root(): # path operation function
    return {"message": "Hello World"}


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Item(BaseModel):
    name: str
    description: str
    price: float
    tax: float | None = None
    supplier: str | None = None

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}

def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id

@app.get("/films/")
async def read_items(
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None,
):
    if id:
        film = data.get(id)
    else:
        id, film = random.choice(list(data.items()))
    return {"id": id, "name": film}

# Order matters
# The first one will always be used since the path matches first.

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep learning FTW!"}

    if model_name == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "have some residuals"}


fake_items_db = [{"item_name: Xoo"}, {"item_name": "Bar"}, {"item_name": "Taz"}]


@app.get("/items/")
async def read_item(q: Annotated[list[str] | None, Query(title="Query string",
                                                         description="Query string for the items to search in the database that have a good match",
                                                         alias="item-query",
                                                         pattern="^[a-z0-9-]+$",
                                                         deprecated=False,
                                                         min_length=3, max_length=50) ] = ["me", "her"]):
    if q:
        return {"item": fake_items_db, "q": q}
    return {"item": fake_items_db}

@app.post("/items/{item_id}")
async def create_item(item_id: Annotated[int, Path(title="The ID of the item to get")],
                      item: Item,
                      size: Annotated[float, Query(gt=0, le=10)],
                      q: Annotated[str | None, Query(alias="item-query")] = None):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    if q:
        item_dict.update({"q": q})
    return {"item_id": item_id, "size": size, **item_dict}


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False):

    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
