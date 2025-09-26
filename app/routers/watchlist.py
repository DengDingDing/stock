"""
API Endpoints for user watchlist management.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas, models
from ..database import get_db

router = APIRouter(
    prefix="/users/{user_id}/watchlist",
    tags=["watchlist"],
)

@router.get("", response_model=List[schemas.UserWatchlistResponse])
async def read_user_watchlist(user_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a user's watchlist."""
    # In a real app, you would first verify the user_id belongs to the authenticated user.
    watchlist = await crud.get_user_watchlist(db, user_id=user_id)
    return watchlist

@router.post("", response_model=schemas.UserWatchlistResponse)
async def add_to_watchlist(
    user_id: int, 
    item: schemas.UserWatchlistCreate, 
    db: AsyncSession = Depends(get_db)
):
    """Add a stock to a user's watchlist by symbol."""
    stock_info = await crud.get_stock_info_by_symbol(db, symbol=item.symbol)
    if not stock_info:
        # Optionally, you could create the stock_info record here
        raise HTTPException(status_code=404, detail=f"Stock with symbol {item.symbol} not found.")

    # Check if it's already in the watchlist
    existing_watchlist = await crud.get_user_watchlist(db, user_id=user_id)
    if any(w.stock_id == stock_info.id for w in existing_watchlist):
        raise HTTPException(status_code=400, detail="Stock already in watchlist")

    new_item = await crud.add_stock_to_watchlist(db, user_id=user_id, stock_id=stock_info.id)
    # We need to manually load the relationship for the response model
    response = await crud.get_user_watchlist(db, user_id=user_id) # Re-fetch to populate relationship
    return next(w for w in response if w.id == new_item.id)


@router.delete("/{symbol}")
async def remove_from_watchlist(user_id: int, symbol: str, db: AsyncSession = Depends(get_db)):
    """Remove a stock from a user's watchlist by symbol."""
    stock_info = await crud.get_stock_info_by_symbol(db, symbol=symbol)
    if not stock_info:
        raise HTTPException(status_code=404, detail=f"Stock with symbol {symbol} not found.")

    success = await crud.remove_stock_from_watchlist(db, user_id=user_id, stock_id=stock_info.id)
    if not success:
        raise HTTPException(status_code=404, detail="Stock not found in watchlist")
    
    return {"message": "Stock removed from watchlist successfully"}
