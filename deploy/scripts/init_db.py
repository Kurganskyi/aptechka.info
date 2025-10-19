"""
Скрипт инициализации БД с тестовыми данными
"""

import asyncio
from datetime import datetime
from loguru import logger

from src.config.settings import settings
from src.config.logging import setup_logging
from src.infrastructure.database.connection import db_connection
from src.infrastructure.database.models import Base
from src.infrastructure.database.models.product import ProductModel
from src.infrastructure.database.models.faq import FAQItemModel


async def init_database():
    """Инициализация БД"""
    try:
        # Настройка логирования
        setup_logging()
        logger.info("Initializing database...")
        
        # Инициализация подключения к БД
        await db_connection.initialize()
        
        # Создание таблиц
        async with db_connection.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created")
        
        # Добавление тестовых данных
        await add_test_data()
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        await db_connection.close()


async def add_test_data():
    """Добавление тестовых данных"""
    try:
        async with db_connection.get_session() as session:
            # Проверяем, есть ли уже данные
            result = await session.execute("SELECT COUNT(*) FROM products")
            count = result.scalar()
            
            if count > 0:
                logger.info("Test data already exists, skipping...")
                return
            
            # Добавляем продукты
            products = [
                ProductModel(
                    slug="tripwire_1byn",
                    name="Трипвайер за 1 BYN",
                    description="Видео с базовой информацией об аптечках",
                    price_kopecks=100,  # 1 BYN в копейках
                    file_id=None,  # TODO: Загрузить файл в Telegram
                    file_type="video",
                    is_active=True,
                    sort_order=1,
                ),
                ProductModel(
                    slug="tripwire_99byn",
                    name="Трипвайер за 99 BYN",
                    description="Расширенное видео с подробной информацией",
                    price_kopecks=9900,  # 99 BYN в копейках
                    file_id=None,  # TODO: Загрузить файл в Telegram
                    file_type="video",
                    is_active=True,
                    sort_order=2,
                ),
                ProductModel(
                    slug="guide_1byn",
                    name="Гайд за 1 BYN",
                    description="PDF гайд с базовой информацией",
                    price_kopecks=100,  # 1 BYN в копейках
                    file_id=None,  # TODO: Загрузить файл в Telegram
                    file_type="document",
                    is_active=True,
                    sort_order=3,
                ),
                ProductModel(
                    slug="kit_family",
                    name="Семейная аптечка на год",
                    description="Полная аптечка для семьи на год",
                    price_kopecks=14900,  # 149 BYN в копейках
                    file_id=None,  # TODO: Загрузить файл в Telegram
                    file_type="document",
                    is_active=True,
                    sort_order=4,
                ),
                ProductModel(
                    slug="kit_summer",
                    name="Летняя-весенняя аптечка",
                    description="Аптечка для теплого времени года",
                    price_kopecks=4900,  # 49 BYN в копейках
                    file_id=None,  # TODO: Загрузить файл в Telegram
                    file_type="document",
                    is_active=True,
                    sort_order=5,
                ),
                ProductModel(
                    slug="kit_child",
                    name="Детская аптечка",
                    description="Специальная аптечка для детей",
                    price_kopecks=4900,  # 49 BYN в копейках
                    file_id=None,  # TODO: Загрузить файл в Telegram
                    file_type="document",
                    is_active=True,
                    sort_order=6,
                ),
                ProductModel(
                    slug="kit_vacation",
                    name="Аптечка в отпуск",
                    description="Компактная аптечка для путешествий",
                    price_kopecks=4900,  # 49 BYN в копейках
                    file_id=None,  # TODO: Загрузить файл в Telegram
                    file_type="document",
                    is_active=True,
                    sort_order=7,
                ),
            ]
            
            for product in products:
                session.add(product)
            
            # Добавляем FAQ
            faq_items = [
                FAQItemModel(
                    question="Где купить лекарства?",
                    answer="В нашем каталоге подберем доступные препараты, которые есть в любой аптеке. Как происходит менеджер по приобретению. Если лекарств с разными рецептами хранения. Пакет для анализа - если чего-то нет в наличии.",
                    sort_order=1,
                    is_active=True,
                ),
                FAQItemModel(
                    question="Актуальность аптечек",
                    answer="В следующем смогу на вопросы приоритизации по мы не исследуем на эффект задержки, поэтому у каждой аптеки выбраны только лучшие препараты для организации хранения лекарств.",
                    sort_order=2,
                    is_active=True,
                ),
                FAQItemModel(
                    question="Сколько стоят лекарства?",
                    answer="Стоимость лекарств зависит от выбранной аптечки. Мы подбираем препараты разных ценовых категорий для оптимального соотношения цена/качество.",
                    sort_order=3,
                    is_active=True,
                ),
                FAQItemModel(
                    question="Как выглядит аптечка?",
                    answer="Каждая аптечка включает подробное описание с фотографиями, список препаратов с инструкциями по применению и рекомендации по хранению.",
                    sort_order=4,
                    is_active=True,
                ),
                FAQItemModel(
                    question="Свой вопрос",
                    answer="Если у вас есть другие вопросы, напишите их в чат, и мы обязательно ответим!",
                    sort_order=5,
                    is_active=True,
                ),
            ]
            
            for faq_item in faq_items:
                session.add(faq_item)
            
            await session.commit()
            logger.info("Test data added successfully")
            
    except Exception as e:
        logger.error(f"Error adding test data: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init_database())
