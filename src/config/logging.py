"""
Конфигурация логирования
"""

import sys
from loguru import logger
from src.config.settings import settings


def setup_logging():
    """Настройка системы логирования"""
    
    # Удаляем стандартный handler
    logger.remove()
    
    # Консольный вывод
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True if not settings.is_production else False,
    )
    
    # Файловое логирование для production
    if settings.is_production:
        logger.add(
            "logs/bot_{time:YYYY-MM-DD}.log",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="1 day",
            retention="30 days",
            compression="zip",
        )
        
        # Отдельный файл для ошибок
        logger.add(
            "logs/errors_{time:YYYY-MM-DD}.log",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="1 day",
            retention="90 days",
            compression="zip",
        )
    
    # Настройка логирования для внешних библиотек
    import logging
    
    # aiogram
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    
    # aiohttp
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    
    # asyncpg
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    
    return logger
