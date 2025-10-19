"""
Настройки приложения с валидацией через Pydantic
"""

from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram Bot
    bot_token: str = Field(..., env="BOT_TOKEN")
    admin_telegram_ids: List[int] = Field(default_factory=list, env="ADMIN_TELEGRAM_IDS")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    db_pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    
    # bePaid Payment System
    bepaid_shop_id: str = Field(..., env="BEPAID_SHOP_ID")
    bepaid_secret_key: str = Field(..., env="BEPAID_SECRET_KEY")
    bepaid_api_url: str = Field(default="https://api.bepaid.by", env="BEPAID_API_URL")
    bepaid_webhook_secret: str = Field(..., env="BEPAID_WEBHOOK_SECRET")
    
    # Application
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    webhook_host: Optional[str] = Field(default=None, env="WEBHOOK_HOST")
    webhook_port: int = Field(default=8080, env="WEBHOOK_PORT")
    
    # External Services
    reviews_chat_url: str = Field(..., env="REVIEWS_CHAT_URL")
    support_chat_url: str = Field(..., env="SUPPORT_CHAT_URL")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    allowed_hosts: List[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"], env="ALLOWED_HOSTS")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    @validator("admin_telegram_ids", pre=True)
    def parse_admin_ids(cls, v):
        """Парсинг списка ID админов из строки"""
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v
    
    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v):
        """Парсинг списка разрешенных хостов"""
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Валидация уровня логирования"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @property
    def is_production(self) -> bool:
        """Проверка production окружения"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Проверка development окружения"""
        return self.environment.lower() == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings()
