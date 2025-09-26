"""
Application configuration management.

Loads settings from environment variables and/or a .env file.
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Defines application settings, loaded from environment variables.
    """
    # Default to a local SQLite DB for ease of setup, but MySQL is recommended for production.
    DATABASE_URL: str = "mysql+aiomysql://user:password@localhost:3306/stock_db"
    BAOSTOCK_USERNAME: str = "your_baostock_username"
    BAOSTOCK_PASSWORD: str = "your_baostock_password"

    class Config:
        # Load settings from a .env file
        env_file = ".env"

# Create a single, reusable instance of the settings
settings = Settings()
