"""LimeStar Configuration Management"""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

# 查找项目根目录的 .env 文件
ROOT_DIR = Path(__file__).parent.parent.parent  # backend/app/config.py -> limestar/
ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "LimeStar"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./limestar.db"

    # OpenAI API (支持自定义 base_url, model, api_key)
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"

    # Telegram Bot (Phase 7)
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    WEBHOOK_URL: Optional[str] = None

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
settings = Settings()
