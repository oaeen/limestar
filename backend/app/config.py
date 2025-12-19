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
    TELEGRAM_ALLOWED_USERS: str = ""  # 逗号分隔的用户 ID 列表
    WEBHOOK_URL: Optional[str] = None

    # Web Admin Authentication
    WEB_ADMIN_PASSWORD: str = ""  # Web 管理密码，为空则禁用 Web 管理功能

    def get_allowed_users(self) -> list[int]:
        """解析白名单用户 ID 列表"""
        if not self.TELEGRAM_ALLOWED_USERS:
            return []
        return [int(uid.strip()) for uid in self.TELEGRAM_ALLOWED_USERS.split(",") if uid.strip()]

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
settings = Settings()
