"""
Main FastAPI application entry point.

This file configures and initializes the FastAPI application, including routers.
"""
from fastapi import FastAPI
from .database import Base, async_engine
from .routers import stock, watchlist

app = FastAPI(
    title="Stock Trading & Visualization System",
    description="A backend system for fetching, storing, and serving stock market data.",
    version="1.0.0",
)

@app.on_event("startup")
async def startup():
    """Create database tables on startup."""
    async with async_engine.begin() as conn:
        # Use this to create tables. In production, you'd use Alembic migrations.
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

# Include the routers
app.include_router(stock.router)
app.include_router(watchlist.router)

@app.get("/")
async def root():
    """Root endpoint providing a welcome message."""
    return {"message": "Welcome to the Stock Trading & Visualization System API"}
