"""Application configuration management."""
import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Project root (shortURL/)
ROOT_DIR = Path(__file__).resolve().parent.parent

# Determine environment
ENV = os.getenv("ENV", "local") # 'local', by default

# Map ENV → env file
ENV_FILE_MAP = {
    "local": ".env.local",
    "test": ".env.test",
    "production": ".env.production",
}

env_file = ENV_FILE_MAP.get(ENV)

# Load environment variables
if env_file:
    load_dotenv(ROOT_DIR / env_file)
else:
    raise RuntimeError(f"Invalid ENV value: {ENV}")


class Settings:
    """Application settings and configuration."""

    # Environment
    ENV: str = ENV
    
    # Application
    APP_NAME: str = "URL Shortener"
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', '8001'))
    
    # Security
    SECRET_KEY: str = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', str(60 * 24 * 7)))
    
    # CORS
    CORS_ORIGINS: list = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Ensure data directory exists
    DATA_DIR = ROOT_DIR / "data"
    DATA_DIR.mkdir(exist_ok=True)
    
    # Database
    DB_PATH: Path = ROOT_DIR / os.getenv('DB_PATH', 'data/url_shortener.db')
    
    # Short Code
    SHORT_CODE_LENGTH: int = int(os.getenv('SHORT_CODE_LENGTH', '6'))
    SHORT_CODE_MIN_LENGTH: int = 2
    SHORT_CODE_MAX_LENGTH: int = 20
    
    # Cookie settings
    COOKIE_NAME: str = "access_token"
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"


settings = Settings()