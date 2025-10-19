#!/bin/bash

# Настройка переменных окружения для разработки
export BOT_TOKEN="8220071391:AAF3z2o1RC3m6yn6XiCUWX1fNcx9WH0EILA"
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/aptechka"
export BEPAID_SHOP_ID="test_shop_id"
export BEPAID_SECRET_KEY="test_secret_key"
export BEPAID_API_URL="https://api.bepaid.by"
export BEPAID_WEBHOOK_SECRET="test_webhook_secret"
export ADMIN_TELEGRAM_IDS="123456789,987654321"
export REVIEWS_CHAT_URL="https://t.me/test_reviews"
export SUPPORT_CHAT_URL="https://t.me/test_support"
export SECRET_KEY="development_secret_key_12345"
export LOG_LEVEL="INFO"
export ENVIRONMENT="development"
export DEBUG="true"

# Активация виртуального окружения
source ~/aptechka-venv/bin/activate

# Переход в директорию проекта
cd /mnt/c/Users/kurga/Desktop/aptechka.info

# Запуск бота
python -m src.main
