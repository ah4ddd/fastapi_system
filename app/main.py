from fastapi import FastAPI
from app.routers import items # type: ignore
from . import database as db

app = FastAPI(
    title="FastAPI System",
    description="A production-ready CRUD API with async support",
    version="1.0.0"
)

# Take all routes registered on this router and attach them to the main app
app.include_router(items.router)

# Root endpoints
@app.get("/")
async def read_root():
    return {"message": "System is alive"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "total_items": len(db.items_db)
    }

