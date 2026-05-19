from fastapi import FastAPI
from pydantic import BaseModel

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

@app.post("/user/")
async def user(user: User):
    return f"welcome {user.name}"
