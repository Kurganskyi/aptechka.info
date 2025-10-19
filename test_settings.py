#!/usr/bin/env python3
"""
Тест настроек
"""

import os
import sys

# Настройка переменных окружения
os.environ['BOT_TOKEN'] = '8220071391:AAF3z2o1RC3m6yn6XiCUWX1fNcx9WH0EILA'
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/aptechka'
os.environ['BEPAID_SHOP_ID'] = 'test_shop'
os.environ['BEPAID_SECRET_KEY'] = 'test_key'
os.environ['BEPAID_API_URL'] = 'https://api.bepaid.by'
os.environ['BEPAID_WEBHOOK_SECRET'] = 'test_webhook_secret'
os.environ['ADMIN_TELEGRAM_IDS'] = '123456789,987654321'
os.environ['REVIEWS_CHAT_URL'] = 'https://t.me/test_reviews'
os.environ['SUPPORT_CHAT_URL'] = 'https://t.me/test_support'
os.environ['SECRET_KEY'] = 'test_secret_key_12345'
os.environ['LOG_LEVEL'] = 'INFO'
os.environ['ENVIRONMENT'] = 'development'
os.environ['DEBUG'] = 'true'
os.environ['WEBHOOK_PATH'] = '/webhook/bepaid'

# Убираем лишние переменные
for key in list(os.environ.keys()):
    if 'ADMIN_IDS' in key and key != 'ADMIN_TELEGRAM_IDS':
        del os.environ[key]

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Импорт настроек...")
    from src.config.settings import settings
    print("✅ Настройки загружены успешно!")
    print(f"Токен бота: {settings.bot_token[:20]}...")
    print(f"ID админов: {settings.admin_ids_list}")
    print(f"База данных: {settings.database_url}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
