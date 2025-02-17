# Backend/app/utils/config.py
import os
from pydantic import BaseSettings
from fastapi import Depends

class Settings(BaseSettings):
    openai_api_key: str
    GOOGLE_API_KEY: str
    GOOGLE_CSE_ID: str


    class Config:
        env_file = ".env"  # Load environment variables from a .env file

settings = Settings()  # Load all settings at once

def get_settings() -> Settings:
    return settings