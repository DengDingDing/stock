"""
Pydantic models (schemas) for data validation and serialization.

These models define the shape of the data for API requests and responses.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

# Pydantic models should be configured to work with ORM objects.
class Config:
    from_attributes = True

# --- StockDailyData Schemas ---
class StockDailyDataBase(BaseModel):
    trade_date: date
    open_price: Decimal = Field(..., description="Post-adjusted opening price")
    high_price: Decimal = Field(..., description="Post-adjusted highest price")
    low_price: Decimal = Field(..., description="Post-adjusted lowest price")
    close_price: Decimal = Field(..., description="Post-adjusted closing price")
    volume: int
    amount: Optional[int] = None

class StockDailyDataCreate(StockDailyDataBase):
    pass

class StockDailyDataResponse(StockDailyDataBase):
    id: int
    stock_id: int
    model_config = Config

# --- StockInfo Schemas ---
class StockInfoBase(BaseModel):
    symbol: str = Field(..., max_length=10)
    company_name: Optional[str] = Field(None, max_length=255)
    exchange: Optional[str] = Field(None, max_length=50)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    ipo_date: Optional[date] = None

class StockInfoCreate(StockInfoBase):
    pass

class StockInfoResponse(StockInfoBase):
    id: int
    last_updated: datetime
    model_config = Config

class StockInfoWithDailyDataResponse(StockInfoResponse):
    daily_data: List[StockDailyDataResponse] = []

# --- User Schemas ---
class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: str = Field(..., max_length=255)

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = Config

# --- UserWatchlist Schemas ---
class UserWatchlistBase(BaseModel):
    user_id: int
    stock_id: int

class UserWatchlistCreate(BaseModel):
    symbol: str # Use symbol to add to watchlist for user convenience

class UserWatchlistResponse(BaseModel):
    id: int
    user_id: int
    stock_id: int
    added_at: datetime
    stock_info: StockInfoResponse
    model_config = Config
