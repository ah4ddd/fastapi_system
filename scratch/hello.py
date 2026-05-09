from fastapi import FastAPI, Query, Path, Body, Cookie, Header
from enum import Enum
from pydantic import BaseModel, AfterValidator, Field, HttpUrl, EmailStr
from typing import Annotated, Any, Literal
from datetime import datetime, time, timedelta
from uuid import UUID
import random


app = FastAPI()

@app.get("/") # path operation decorator
async def root(): # path operation function
    return {"message": "Hello World"}


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Image(BaseModel):
    url: HttpUrl = Field(examples=["https://pin.it/1Gh7RZrSl"])
    name: str = Field("just Name")

class User(BaseModel):
    username: str = Field(examples=["Seeyaah"])
    full_name: str | None = Field(None, examples= ["Fill yourself"])

@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images

class Item(BaseModel):
    name: str = Field(examples=["Sia"])
    description: str = Field(description="The description of the item",
                             max_length=300,
                             min_length=10,
                             examples=["Nice Item"])
    price: float = Field(gt=0, examples=[99999.99])
    tax: float | None = Field(None, gt=0, lt=40, examples=[3.9])
    supplier: str | None = Field(None, min_length=3,
                                 max_length=20,
                                 examples= ["Ahad"])
    images: list[Image]  | None

class Offer(BaseModel):
    name: str = Field(examples=["Div"])
    description: str | None  = Field(None, examples=["good description"])
    price: float = Field(examples=[7.5])
    items: list[Item]

class Cookies(BaseModel):
    model_config = {"extra": "forbid"}
    session_id: str
    fatebook_db: str | None = None
    googall_tracker: str | None = None

class CommonHeaders(BaseModel):
    model_config = {"extra": "forbid"}
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []


@app.post("/offers/")
async def create_offer(offer: Offer,
                       header: Annotated[CommonHeaders, Header()],
                       cookies: Annotated[Cookies | None, Cookie()] = None):
    return {"offer": offer, "cookies": cookies, "header": header}


@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]) -> dict:
    return weights


class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

class UserIn(BaseUser):
    password: str

#dont fuck this in prod
@app.post("/user/", response_model=BaseUser)
async def create_user(user: UserIn) -> BaseUser:
    return user


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


class FilterParameter(BaseModel):
    model_config = {"extra": "forbid"}

    limit : int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: set[str] = set()

@app.get("/filtered-items")
async def f_item(filter_query: Annotated[FilterParameter, Query()]) -> FilterParameter:
    return filter_query

@app.put("/time/{time_id}/")
async def read_time(
    time_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
    repeat_at: Annotated[time | None, Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return{
        "time_id": time_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }

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
                      item: Annotated[Item, Body(embed=True)],
                      user: User,
                      size: Annotated[float, Query(gt=0, le=10)],
                      importance: Annotated[int, Body()],
                      q: Annotated[str | None, Query(alias="item-query")] = None):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    if q:
        item_dict.update({"q": q})
    return {"item_id": item_id,
            "user": user,
            "size": size,
            "importance": importance,
            **item_dict}


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
