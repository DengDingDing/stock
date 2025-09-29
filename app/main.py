"""
Main FastAPI application entry point.

This file configures and initializes the FastAPI application, including routers.
FastAPI应用程序的主入口点。

该文件用于配置和初始化FastAPI应用，包括路由器的设置。
"""
from fastapi import FastAPI
from .database import Base, async_engine
# .代表包目录内部的相对导入
from .routers import stock, watchlist

app = FastAPI(
    title="Stock Trading & Visualization System",
    description="A backend system for fetching, storing, and serving stock market data.",
    version="1.0.0",
)

@app.on_event("startup")
# 第一行是“异步地打开数据库连接并进入事务”。
# 第二行是“在这个连接上，等待表结构创建完成”。
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
    """提供欢迎信息的根端点。"""
    return {"message": "Welcome to the Stock Trading & Visualization System API"}
