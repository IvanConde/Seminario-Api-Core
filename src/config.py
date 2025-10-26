"""Configuration settings for Core API."""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "unified_messaging"
    db_user: str = "root"
    db_password: str = ""
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8003
    
    # Core settings
    core_secret_key: str = "your-secret-key-here"
    
    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
