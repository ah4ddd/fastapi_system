from fastapi import FastAPI, Query, Path, Body, Cookie, Header, status, Form, File, UploadFile, HTTPException, Request, Depends
from enum import Enum
from pydantic import BaseModel, AfterValidator, Field, HttpUrl, EmailStr
from typing import Annotated, Any, Literal
from datetime import datetime, time, timedelta
from uuid import UUID
import random
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

app = FastAPI()

@app.get("/") # path operation decorator
async def root(): # path operation function
    return {"message": "Hello World"}


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

so_fake_db ={}

class EncodeThisItem(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None

@app.put("/encode/{id}")
async def encoder(id: str, item: EncodeThisItem):
    json_compatible_item_data = jsonable_encoder(item)
    so_fake_db[id] = json_compatible_item_data

class Image(BaseModel):
    url: HttpUrl = Field(examples=["https://pin.it/1Gh7RZrSl"])
    name: str = Field("just Name")

class User(BaseModel):
    username: str = Field(examples=["Seeyaah"])
    full_name: str | None = Field(None, examples= ["Fill yourself"])

@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images

# MY OWN custom exception type
class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

# global handler for UnicornException
# The same concept as route() but for exceptions,
# instead of routes. When THIS exception gets raised anywhere
# in the app, run this function instead of crashing.
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=status.HTTP_418_IM_A_TEAPOT,
        content={"message": f"fck!  {exc.name} did something so wrong."}
    )

@app.get("/unicorns/{name}")
async def read_unicorn(name:str):
    if name == "siya":
        raise UnicornException(name=name)
    return {"unicorn_name": name}


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
    price: float = Field(gt=0, examples=[7.5])
    items: list[Item]

@app.post("/offers")
async def create_offer(offers: Offer):
    return {"offers": offers}


class Game(BaseModel):
    title: str
    full_name: str

games_db = {
    "mgs3": {
        "title": "mgs3",
        "full_name": "Metal Gear Solid 3: Snake Eater"
    },
    "gow3": {
        "title": "gow3",
        "full_name": "God of War III"
    },
    "sh2": {
        "title": "sh2",
        "full_name": "Silent Hill 2"
    }
}

@app.get("/games/", tags=["games"])
async def games():
    return games_db

@app.get("/games/{game_id}",
         response_model=Game,
         tags=["games"],
         response_description="your game")
async def read_game(game_id: str):
    """
    ## 🎮 Get Game

    Retrieve a game using its ID.

    ### Example
    - `mgsv`
    - `gow3`

    ### Raises
    - `404` if game is not found
    """
    if game_id not in games_db:
        raise HTTPException(
            status_code=404,
            detail="Game not found",
            headers={"Error": "There goes my error"},
                            )
    return games_db[game_id]

@app.put("/games/", response_model=Game, tags=["games"])
async def update_games(games: Game):
    games_encoded = jsonable_encoder(games)
    games_db[games.title] = games_encoded
    return games_encoded

class GameUpdate(BaseModel):
    title: str | None = None
    full_name: str | None = None

@app.patch("/games/{game_id}", response_model=Game, tags=["games"])
async def patch_update_game(game_id: str, game: GameUpdate):
    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")
    store_game_data = games_db[game_id]
    store_game_model = Game(**store_game_data)
    # Only include fields user ACTUALLY sent. No None
    update_game = game.model_dump(exclude_unset=True)
    # Take old object + overwrite changed fields = new object
    updated_game = store_game_model.model_copy(update=update_game)
    games_db[game_id] = jsonable_encoder(updated_game)
    return updated_game

@app.delete("/games/", status_code=204, tags=["games"])
async def delete_game(game_id: str):
    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")
    del games_db[game_id]

async def query_extractor(q: str | None = None):
    return q

# dependency function
async def common_parameters(q: Annotated[str, Depends(query_extractor)],
                            skip: int = 0,
                            limit: int = 100):
    if not q:
        return {"skip": skip, "limit": limit}
    return {"q": q, "skip": skip, "limit": limit}

CommonsDep = Annotated[dict, Depends(common_parameters)]

@app.get("/read-users/")
async def read_users(commons: CommonsDep):
    return commons


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 4):
        self.q = q
        self.skip = skip
        self.limit = limit

q = CommonQueryParams("q", 1, 2)
print(q.q, q.limit, q.skip)

fake_items_db = [{"item_name": "Ursaal"},
                 {"item_name": "Marcus"},
                 {"item_name": "Rex"}]

@app.get("/read-item/")
# shortcut — FastAPI infers the dependency from the type annotation aswell
async def read__items(commons: Annotated[CommonQueryParams, Depends()]):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip: commons.skip + commons.limit]
    response.update({"items": items})
    return response

async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret_token":
        raise HTTPException(status_code=400, detail="X-key header invalid")

async def verify_key(x_key: Annotated[str, Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-token header invalid")
    return x_key

@app.get("/tokens/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_tokens():
    """
    Before endpoint executes:
    read_items()

    FastAPI first executes:
    verify_token()
    verify_key()

    IF BOTH PASS:
    endpoint runs.

    IF ONE FAILS:
    endpoint NEVER runs.
    """

    return [{"item": "Monax"}, {"item": "Terra"}]


test_data = {
    "plumbus": {"description": "Freshly pickled plumbus", "owner": "Morty"},
    "portal-gun": {"description": "Gun to create portals", "owner": "Rick"},
    }

class OwnerError(Exception):
    pass


def get_username():
    try:
        yield "Morty"
    finally:
        print("Cleaned up before response is sent")


@app.get("/owned/me")
def get_user_me(username: Annotated[str, Depends(get_username, scope="function")]):
    return username

@app.get("/owned/{owned_id}")
def get_item(
    owned_id: str,
    username: Annotated[str, Depends(get_username)]
    ):
    if owned_id == "portal-gun":
        raise HTTPException(status_code=400, detail=f"The portal gun is too dangerous to be owned by {username}")
    if owned_id != "plumbus":
        raise HTTPException(status_code=404,
                            detail="Item not found, there's only a plumbus here")
    return owned_id


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


@app.post("/cookie-header/", status_code=status.HTTP_201_CREATED)
async def create_cookie_header(header: Annotated[CommonHeaders, Header()],
                       cookies: Annotated[Cookies | None, Cookie()] = None):
        return {
            "cookies": cookies,
            "header": header
                }


@app.post("/index-weights/", deprecated=True)
async def create_index_weights(weights: dict[int, float]) -> dict:
    return weights

@app.post("/file/", tags=["files"], description="Upload a file it doesnt do much")
async def create_file(file: Annotated[bytes, File(),],
                      fileb: Annotated[UploadFile, File()],
                      token: Annotated[str, Form()],
                      caption: Annotated[str, Form()],
                      ):
    return {"file_size": len(file),
            "token": token,
            "file_content_type": fileb.content_type,
            "caption": caption}

@app.post("/upload-file/", status_code=status.HTTP_201_CREATED, tags=["files"])
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str

def fake_pw_hash(raw_password: str):
    return "supersecret" + raw_password

def fake_save_user(user_in: UserIn):
    hashed_password = fake_pw_hash(user_in.password)
    user_in_db = UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db


@app.post("/user/", response_model=UserOut, status_code=201, response_description="created fake user")
async def create_user(user_in: UserIn) -> Any:
    user_saved = fake_save_user(user_in)
    return user_saved


class FormData(BaseModel):
    username: str
    password: str
    model_config= {"extra":"forbid"}

@app.post("/login/")
async def login(data: Annotated[FormData, Form()]):
    return data


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

fake_db = [{"item_name: Xoo"}, {"item_name": "Bar"}, {"item_name": "Taz"}]

@app.get("/items/")
async def read_item(q: Annotated[list[str] | None, Query(title="Query string",
                                                         description="Query string for the items to search in the database that have a good match",
                                                         alias="item-query",
                                                         pattern="^[a-z0-9-]+$",
                                                         deprecated=False,
                                                         min_length=3, max_length=50) ] = ["me", "her"]):
    if q:
        return {"item": fake_db, "q": q}
    return {"item": fake_db}


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
