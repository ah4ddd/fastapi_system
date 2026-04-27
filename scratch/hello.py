from fastapi import FastAPI

app = FastAPI()

@app.get("/") # path operation decorator
async def root(): # path operation function
    return {"message": "Hello World"}

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

