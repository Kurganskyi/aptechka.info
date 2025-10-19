#!/bin/bash

# Скрипт развертывания для dev среды

set -e

echo "🚀 Starting dev deployment..."

# Переменные
PROJECT_NAME="aptechka-bot-dev"
DOCKER_COMPOSE_FILE="docker-compose.dev.yml"
ENV_FILE=".env.dev"

# Проверка наличия файлов
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    echo "❌ Docker compose file not found: $DOCKER_COMPOSE_FILE"
    exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Environment file not found: $ENV_FILE"
    exit 1
fi

# Остановка существующих контейнеров
echo "🛑 Stopping existing containers..."
docker-compose -f $DOCKER_COMPOSE_FILE down

# Обновление образов
echo "📦 Pulling latest images..."
docker-compose -f $DOCKER_COMPOSE_FILE pull

# Запуск контейнеров
echo "🏗️ Starting containers..."
docker-compose -f $DOCKER_COMPOSE_FILE up -d

# Ожидание готовности БД
echo "⏳ Waiting for database to be ready..."
sleep 10

# Проверка здоровья БД
echo "🔍 Checking database health..."
until docker exec aptechka_db_dev pg_isready -U aptechka_user -d aptechka_dev; do
    echo "Waiting for database..."
    sleep 2
done

# Применение миграций
echo "📊 Applying database migrations..."
py -m alembic upgrade head

# Инициализация БД с тестовыми данными
echo "🎯 Initializing database with test data..."
py deploy/scripts/init_db.py

# Проверка здоровья сервисов
echo "🏥 Checking services health..."
sleep 5

# Проверка webhook сервера
if curl -f http://localhost:8080/health; then
    echo "✅ Webhook server is healthy"
else
    echo "⚠️ Webhook server health check failed"
fi

# Проверка БД
if docker exec aptechka_db_dev pg_isready -U aptechka_user -d aptechka_dev; then
    echo "✅ Database is healthy"
else
    echo "⚠️ Database health check failed"
fi

echo "🎉 Dev deployment completed successfully!"
echo ""
echo "📋 Service URLs:"
echo "  - Webhook server: http://localhost:8080"
echo "  - Database: localhost:5432"
echo ""
echo "📝 Useful commands:"
echo "  - View logs: make logs-dev"
echo "  - Stop services: make stop-dev"
echo "  - Restart services: make dev"
