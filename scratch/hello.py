from fastapi import FastAPI
from enum import Enum

app = FastAPI()

"""
When you DO need it in FastAPI:
When the value is coming from a URL path, query param, or request body — FastAPI needs to parse a raw string/int from the request into your enum.
"""
# str in the parameter = member behaves like a normal string everywhere,
# no .value needed, no ugly repr, just works.
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/") # path operation decorator
async def root(): # path operation function
    return {"message": "Hello World"}

# Order matters
# The first one will always be used since the path matches first.

@app.get("users/me")
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id):
    return {"user_id": user_id}


@app.get("/items/{item_id}")
# with the same Python type declaration, FastAPI give you data validation.
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep learning FTW!"}

    if model_name == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "have some residuals"}


"""
Request
↓
Uvicorn (server receives request)
↓
ASGI interface
↓
Starlette (middleware + routing)
↓
FastAPI (validation + dependency)
↓
Your function (endpoint)
↓
FastAPI (serialize response)
↓
Starlette (middleware)
↓
Uvicorn (send response)
↓
Client
"""

