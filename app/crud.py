"""
CRUD (Create, Read, Update, Delete) operations for the database models.

This module provides a data access layer for interacting with the database.
"""
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.mysql import insert

from . import models, schemas

# --- StockInfo CRUD ---

async def get_stock_info_by_symbol(db: AsyncSession, symbol: str) -> Optional[models.StockInfo]:
    """Retrieves a stock_info record by its symbol."""
    result = await db.execute(select(models.StockInfo).filter(models.StockInfo.symbol == symbol))
    return result.scalars().first()

async def get_or_create_stock_info(db: AsyncSession, symbol: str) -> models.StockInfo:
    """Gets a stock_info record or creates it if it doesn't exist."""
    stock_info = await get_stock_info_by_symbol(db, symbol)
    if not stock_info:
        # Note: Additional fields like company_name should be populated from another API/source.
        stock_info = models.StockInfo(symbol=symbol)
        db.add(stock_info)
        await db.commit()
        await db.refresh(stock_info)
    return stock_info

# --- StockDailyData CRUD ---

async def get_latest_daily_data_date(db: AsyncSession, stock_id: int) -> Optional[date]:
    """Gets the most recent trade_date for a given stock_id."""
    result = await db.execute(
        select(models.StockDailyData.trade_date)
        .filter(models.StockDailyData.stock_id == stock_id)
        .order_by(models.StockDailyData.trade_date.desc())
        .limit(1)
    )
    return result.scalars().first()

async def upsert_daily_data_batch(db: AsyncSession, daily_data_list: List[dict]):
    """
    Batch inserts or updates stock_daily_data records.
    Uses MySQL's ON DUPLICATE KEY UPDATE.
    """
    if not daily_data_list:
        return

    stmt = insert(models.StockDailyData).values(daily_data_list)
    
    # Define the columns to update on duplicate key
    update_on_duplicate = {
        'open_price': stmt.inserted.open_price,
        'high_price': stmt.inserted.high_price,
        'low_price': stmt.inserted.low_price,
        'close_price': stmt.inserted.close_price,
        'volume': stmt.inserted.volume,
        'amount': stmt.inserted.amount,
        'update_time': stmt.inserted.update_time,
    }
    
    final_stmt = stmt.on_duplicate_key_update(**update_on_duplicate)
    
    await db.execute(final_stmt)
    await db.commit()

async def get_daily_data_history(
    db: AsyncSession, stock_id: int, start_date: date, end_date: date
) -> List[models.StockDailyData]:
    """Retrieves the daily data history for a stock within a date range."""
    result = await db.execute(
        select(models.StockDailyData)
        .filter(
            models.StockDailyData.stock_id == stock_id,
            models.StockDailyData.trade_date >= start_date,
            models.StockDailyData.trade_date <= end_date
        )
        .order_by(models.StockDailyData.trade_date.asc())
    )
    return result.scalars().all()

# --- UserWatchlist CRUD ---

async def add_stock_to_watchlist(db: AsyncSession, user_id: int, stock_id: int) -> models.UserWatchlist:
    """Adds a stock to a user's watchlist."""
    watchlist_item = models.UserWatchlist(user_id=user_id, stock_id=stock_id)
    db.add(watchlist_item)
    await db.commit()
    await db.refresh(watchlist_item)
    return watchlist_item

async def remove_stock_from_watchlist(db: AsyncSession, user_id: int, stock_id: int) -> bool:
    """Removes a stock from a user's watchlist."""
    result = await db.execute(
        select(models.UserWatchlist)
        .filter(models.UserWatchlist.user_id == user_id, models.UserWatchlist.stock_id == stock_id)
    )
    item_to_delete = result.scalars().first()
    if item_to_delete:
        await db.delete(item_to_delete)
        await db.commit()
        return True
    return False

async def get_user_watchlist(db: AsyncSession, user_id: int) -> List[models.UserWatchlist]:
    """Retrieves a user's entire watchlist."""
    result = await db.execute(
        select(models.UserWatchlist)
        .filter(models.UserWatchlist.user_id == user_id)
        .options(selectinload(models.UserWatchlist.stock_info)) # Eager load stock_info
    )
    return result.scalars().all()
