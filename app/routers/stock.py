"""
API Endpoints for stock-related data.
"""
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas
from ..database import get_db

# 创建了一个带有前缀 /stocks 和标签 stocks 的路由器。
# 这样，所有通过该路由器注册的接口都会自动带上 /stocks 前缀，并在自动生成的文档中归类到 stocks 标签下。
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
    """获取股票在指定日期范围内的历史每日数据。"""
    stock_info = await crud.get_stock_info_by_symbol(db, symbol=symbol)
    if stock_info is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    daily_data = await crud.get_daily_data_history(
        db, stock_id=stock_info.id, start_date=start_date, end_date=end_date
    )
    return daily_data
