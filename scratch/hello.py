from fastapi import FastAPI

app = FastAPI()

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

