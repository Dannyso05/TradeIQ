from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from dotenv import load_dotenv
import os
from typing import Dict, List, Optional, Any

# Load environment variables from .env file
load_dotenv()

class PortfolioStore:
    """Singleton class to store extracted portfolio data between routes."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PortfolioStore, cls).__new__(cls)
            cls._instance.assets = []
            cls._instance.raw_data = {}
        return cls._instance
    
    def store_portfolio(self, assets: List[Dict[str, Any]]):
        """Store the portfolio assets."""
        self.assets = assets
        
    def store_raw_data(self, data: Dict[str, Any]):
        """Store the raw extracted data."""
        self.raw_data = data
        
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """Get the stored portfolio assets."""
        return self.assets
    
    def get_raw_data(self) -> Dict[str, Any]:
        """Get the raw extracted data."""
        return self.raw_data
    
    def clear(self):
        """Clear the stored data."""
        self.assets = []
        self.raw_data = {}


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Credentials
    openai_api_key: str = Field(env="OPENAI_API_KEY")
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    google_cse_id: str = Field(default="", env="GOOGLE_CSE_ID")
    
    # LLM Settings
    llm_model: str = Field(default="gpt-4o", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.2, env="LLM_TEMPERATURE")
    
    # API settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=3000, env="API_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Create cached settings instance."""
    return Settings()

# Create a singleton instance of the portfolio store
portfolio_store = PortfolioStore() 