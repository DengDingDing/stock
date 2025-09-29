"""
应用程序的SQLAlchemy ORM模型。

这些模型定义了映射到数据库表的Python对象。
"""
import datetime
from typing import List, Optional
from decimal import Decimal

from sqlalchemy import (BigInteger, Column, Date, DateTime, ForeignKey, Numeric,
                        String, Text, UniqueConstraint)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    watchlists: Mapped[List["UserWatchlist"]] = relationship(back_populates="user")

class StockInfo(Base):
    __tablename__ = "stock_info"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), default="")
    exchange: Mapped[Optional[str]] = mapped_column(String(50), default="")
    sector: Mapped[Optional[str]] = mapped_column(String(100), default="")
    industry: Mapped[Optional[str]] = mapped_column(String(100), default="")
    description: Mapped[Optional[str]] = mapped_column(Text)
    ipo_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    last_updated: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    daily_data: Mapped[List["StockDailyData"]] = relationship(back_populates="stock_info")
    watchlists: Mapped[List["UserWatchlist"]] = relationship(back_populates="stock_info")

class StockDailyData(Base):
    __tablename__ = "stock_daily_data"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stock_info.id", ondelete="CASCADE"), nullable=False)
    trade_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    open_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    high_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    low_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    close_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    amount: Mapped[Optional[int]] = mapped_column(BigInteger)
    creation_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    stock_info: Mapped["StockInfo"] = relationship(back_populates="daily_data")

    __table_args__ = (UniqueConstraint("stock_id", "trade_date", name="uq_stock_date"),)

class UserWatchlist(Base):
    __tablename__ = "user_watchlist"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stock_info.id", ondelete="CASCADE"), nullable=False)
    added_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="watchlists")
    stock_info: Mapped["StockInfo"] = relationship(back_populates="watchlists")

    __table_args__ = (UniqueConstraint("user_id", "stock_id", name="uq_user_stock"),)
