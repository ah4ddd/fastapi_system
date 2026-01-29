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
