"""
API Endpoints for stock-related data.
"""
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
)

@router.get("/{symbol}", response_model=schemas.StockInfoResponse)
async def read_stock_info(symbol: str, db: AsyncSession = Depends(get_db)):
    """Retrieve basic information for a single stock by its symbol."""
    stock_info = await crud.get_stock_info_by_symbol(db, symbol=symbol)
    if stock_info is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock_info

@router.get("/{symbol}/daily_data", response_model=List[schemas.StockDailyDataResponse])
async def read_stock_daily_data(
    symbol: str,
    start_date: date = Query(..., description="Start date for the data range (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date for the data range (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve historical daily data for a stock within a given date range."""
    stock_info = await crud.get_stock_info_by_symbol(db, symbol=symbol)
    if stock_info is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    daily_data = await crud.get_daily_data_history(
        db, stock_id=stock_info.id, start_date=start_date, end_date=end_date
    )
    return daily_data
