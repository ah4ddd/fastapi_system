from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()

@app.get("/hello/")
async def hello():
    return {"LETS DO IT FROM SCRATCH"}

@app.post("/items/{item_id}/")
async def items(item_id: str):
    return f"back at yaa!! {item_id}"

class User(BaseModel):
    name: str
    age: int
    country: str | None = None

user_db = {}

@app.post("/user/")
async def user(user: User):
    user_db[user.name.title()] = user.model_dump()
    if user.country:
        return f"Welcom {user.name.title()} from {user.country.title()}"
    return f"welcome {user.name.title()}"

@app.get("/see-users/")
async def users():
    return user_db

@app.delete("/user/")
async def del_user(user: Annotated[str, Body()]):
    username = user.title()
    if username in user_db:
        del user_db[username]
        return {"detail": "User deleted"}
    return {"detail": "User not found"}

@app.post("/addition/")
async def add(a: Annotated[int, Body()], b: Annotated[int, Body()]):
    return a + b

@app.post("/subtraction/")
async def sub(a: Annotated[int, Body()], b: Annotated[int, Body()]):
    return a - b

