"""
Asynchronous tasks for data synchronization.

These functions handle the initial full data sync and daily incremental updates.
They are designed to be run from a scheduler (like APScheduler, Celery, or cron).
"""
import asyncio
import logging
from datetime import date, timedelta
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, baostock_utils, models
from .database import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def initial_full_sync(stock_symbols: List[str], start_date: date):
    """
    Performs an initial, full synchronization of historical data for a list of stocks.

    Args:
        stock_symbols: A list of stock symbols to sync (e.g., ['sh.600000', 'sz.000001']).
        start_date: The date from which to start fetching historical data.
    """
    logger.info(f"Starting initial full sync for {len(stock_symbols)} stocks from {start_date}.")
    async with AsyncSessionLocal() as db:
        for symbol in stock_symbols:
            try:
                logger.info(f"Processing symbol: {symbol}")
                
                # 1. Get or create stock_info record
                stock_info = await crud.get_or_create_stock_info(db, symbol=symbol)
                
                # 2. Fetch historical data from Baostock
                today = date.today()
                df = baostock_utils.fetch_k_data(symbol, start_date=start_date, end_date=today)
                
                if df is not None and not df.empty:
                    # 3. Convert DataFrame to list of dicts for CRUD operation
                    df['stock_id'] = stock_info.id
                    daily_data_list = df.to_dict(orient='records')
                    
                    # 4. Batch upsert into the database
                    await crud.upsert_daily_data_batch(db, daily_data_list=daily_data_list)
                    logger.info(f"Successfully synced {len(daily_data_list)} records for {symbol}.")
                else:
                    logger.warning(f"No data returned for {symbol}. Skipping.")

            except Exception as e:
                logger.error(f"Failed to sync {symbol}: {e}")
                # Continue to the next symbol
                continue
    logger.info("Initial full sync completed.")

async def daily_incremental_sync():
    """
    Performs a daily incremental synchronization for all stocks in the database.
    """
    logger.info("Starting daily incremental sync.")
    async with AsyncSessionLocal() as db:
        # 1. Get all stocks from our database
        result = await db.execute(select(models.StockInfo))
        all_stocks = result.scalars().all()
        
        if not all_stocks:
            logger.warning("No stocks found in the database. Aborting daily sync.")
            return

        for stock_info in all_stocks:
            try:
                logger.info(f"Checking for updates for {stock_info.symbol} (ID: {stock_info.id})")
                
                # 2. Get the last recorded date for the stock
                latest_date = await crud.get_latest_daily_data_date(db, stock_id=stock_info.id)
                
                # 3. Determine the start date for the new fetch
                start_date_for_fetch = (latest_date + timedelta(days=1)) if latest_date else date(1990, 1, 1)
                end_date_for_fetch = date.today()

                if start_date_for_fetch >= end_date_for_fetch:
                    logger.info(f"Data for {stock_info.symbol} is already up to date. Skipping.")
                    continue

                logger.info(f"Fetching data for {stock_info.symbol} from {start_date_for_fetch} to {end_date_for_fetch}")
                
                # 4. Fetch new data
                df = baostock_utils.fetch_k_data(stock_info.symbol, start_date=start_date_for_fetch, end_date=end_date_for_fetch)

                if df is not None and not df.empty:
                    # 5. Convert and save to DB
                    df['stock_id'] = stock_info.id
                    daily_data_list = df.to_dict(orient='records')
                    await crud.upsert_daily_data_batch(db, daily_data_list=daily_data_list)
                    logger.info(f"Successfully synced {len(daily_data_list)} new records for {stock_info.symbol}.")

            except Exception as e:
                logger.error(f"Failed to perform daily sync for {stock_info.symbol}: {e}")
                continue

    logger.info("Daily incremental sync completed.")

# Example of how you might run these tasks
if __name__ == '__main__':
    # This is for demonstration. In a real app, you'd use a scheduler.
    
    # Example: Run initial sync for a few stocks
    # asyncio.run(initial_full_sync(stock_symbols=['sh.600000', 'sz.000001'], start_date=date(2023, 1, 1)))
    
    # Example: Run daily sync
    # asyncio.run(daily_incremental_sync())
    pass
