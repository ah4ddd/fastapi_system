from fastapi import FastAPI
# Loads the items.py file.
from app.routers import items, weather # type: ignore

app = FastAPI( # central server object
    title="FastAPI System",
    description="CRUD API with async support",
    version="1.2.0"
)

# Take all routes registered on this router and attach them to the main app

"""
FastAPI App
│
├── Root
│   ├── GET /
│   └── GET /health
│
└── Items Router
    ├── GET /items
    ├── POST /items
    ├── PUT /items/{id}
    └── DELETE /items/{id}
"""
# include_router(items.router) = Take router.routes & attach them to app.routes
app.include_router(items.router) # items.router → APIRouter instance
app.include_router(weather.router)

# Root endpoints
@app.get("/")
async def read_root():
    return {"message": "System is alive"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }

"""
Full lifecycle (what FastAPI actually does)

When the server starts:

Step 1
Python imports modules
    `main.py imports items module`

Step 2
items.py executes
    `router object created
     routes registered`

Step 3
Main app registers router
    `app.include_router(items.router)`

Step 4
FastAPI merges routes
    `app.routes += router.routes`

Step 5
Server starts listening.
"""

# requests → router → endpoint → validation → business logic → database → response
