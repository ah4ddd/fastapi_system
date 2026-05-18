from fastapi import FastAPI

app = FastAPI()

@app.get("/hello/")
async def hello():
    return {"LETS DO IT FROM SCRATCH"}

@app.post("/items/{item_id}/")
async def items(item_id: str):
    return f"back at yaa!! : {item_id}"
