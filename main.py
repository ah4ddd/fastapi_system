from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "System is alive"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/mission")
def mission():
    return ({"mission":"Learn Fastapi and build cool shit"})

#path parameter
@app.get("/items/{item_id}")
#automatic validation
def read_item(item_id: int): #type hint, validates it's an integar
    return {item_id: item_id, "name": f"Item {item_id}"}
