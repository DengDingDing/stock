"""
应用程序配置管理。

从环境变量和/或.env文件加载设置。
"""
from pydantic_settings import BaseSettings

# 会优先去读取项目根目录的.env文件
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
