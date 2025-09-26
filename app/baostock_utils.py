"""
Utility functions for interacting with the Baostock API.

This module encapsulates login, logout, and data fetching logic.
"""
import baostock as bs
import pandas as pd
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
import logging

from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_is_logged_in = False

def _bs_login():
    """Logs into the Baostock system if not already logged in."""
    global _is_logged_in
    if not _is_logged_in:
        # Here you should use the username and password from settings
        # For this example, we assume they are available.
        # lg = bs.login_by_user(settings.BAOSTOCK_USERNAME, settings.BAOSTOCK_PASSWORD)
        lg = bs.login()
        if lg.error_code == '0':
            _is_logged_in = True
            logger.info("Baostock login successful.")
        else:
            logger.error(f"Baostock login failed: {lg.error_msg}")
            raise ConnectionError(f"Baostock login failed: {lg.error_msg}")

def _bs_logout():
    """Logs out of the Baostock system."""
    global _is_logged_in
    if _is_logged_in:
        bs.logout()
        _is_logged_in = False
        logger.info("Baostock logout successful.")

def fetch_k_data(symbol: str, start_date: date, end_date: date) -> Optional[pd.DataFrame]:
    """
    Fetches historical K-line data for a given stock symbol and date range.

    Args:
        symbol: The stock symbol (e.g., 'sh.600000').
        start_date: The start date for the data query.
        end_date: The end date for the data query.

    Returns:
        A pandas DataFrame with the processed K-line data, or None if no data.
    """
    try:
        _bs_login()
        
        rs = bs.query_history_k_data_plus(
            symbol,
            "date,code,open,high,low,close,volume,amount,adjustflag",
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            frequency="d",
            adjustflag="2" # Use '2' for post-adjustment (后复权)
        )

        if rs.error_code != '0':
            logger.error(f"Baostock query failed for {symbol}: {rs.error_msg}")
            return None

        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            logger.warning(f"No data fetched for {symbol} from {start_date} to {end_date}")
            return None

        df = pd.DataFrame(data_list, columns=rs.fields)

        # --- Data Cleaning and Type Conversion ---
        # Rename columns for consistency
        df.rename(columns={
            'date': 'trade_date',
            'open': 'open_price',
            'high': 'high_price',
            'low': 'low_price',
            'close': 'close_price'
        }, inplace=True)

        # Columns to process
        numeric_cols = ['open_price', 'high_price', 'low_price', 'close_price']
        integer_cols = ['volume', 'amount']

        # Replace empty strings with None for proper conversion
        df.replace('', None, inplace=True)

        # Convert date strings to date objects
        df['trade_date'] = pd.to_datetime(df['trade_date']).dt.date

        # Convert price columns to Decimal for precision
        for col in numeric_cols:
            df[col] = df[col].apply(lambda x: Decimal(str(x)) if pd.notna(x) else None)

        # Convert volume/amount to nullable integers
        for col in integer_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

        return df

    except Exception as e:
        logger.error(f"An error occurred during fetch_k_data for {symbol}: {e}")
        return None
    finally:
        # Logout after each operation to avoid dangling sessions
        _bs_logout()
