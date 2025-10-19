#!/bin/bash

# Скрипт для развертывания Aptechka Bot
# Использование: ./deploy.sh [dev|prod]

set -e

ENVIRONMENT=${1:-dev}
PROJECT_DIR="/opt/aptechka-bot"
SERVICE_NAME="aptechka-bot"

echo "🚀 Deploying Aptechka Bot to $ENVIRONMENT environment..."

# Проверяем, что мы на правильном сервере
if [[ "$ENVIRONMENT" == "prod" ]]; then
    echo "⚠️  Production deployment detected!"
    read -p "Are you sure you want to deploy to production? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

# Создаем директорию проекта если не существует
if [ ! -d "$PROJECT_DIR" ]; then
    echo "📁 Creating project directory..."
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown $USER:$USER "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Останавливаем сервис
echo "🛑 Stopping service..."
sudo systemctl stop "$SERVICE_NAME" || true

# Обновляем Docker images
echo "📥 Pulling latest images..."
docker-compose -f "docker-compose.$ENVIRONMENT.yml" pull

# Запускаем миграции
echo "🗄️  Running database migrations..."
docker-compose -f "docker-compose.$ENVIRONMENT.yml" run --rm bot alembic upgrade head

# Запускаем сервис
echo "▶️  Starting service..."
sudo systemctl start "$SERVICE_NAME"

# Ждем запуска
echo "⏳ Waiting for service to start..."
sleep 10

# Проверяем статус
echo "📊 Service status:"
sudo systemctl status "$SERVICE_NAME" --no-pager

# Проверяем логи
echo "📋 Recent logs:"
sudo journalctl -u "$SERVICE_NAME" --no-pager -n 20

# Проверяем здоровье контейнеров
echo "🏥 Container health check:"
docker-compose -f "docker-compose.$ENVIRONMENT.yml" ps

# Очищаем старые Docker images
echo "🧹 Cleaning up old images..."
docker system prune -f

echo "✅ Deployment completed successfully!"
echo "🔗 Check logs with: sudo journalctl -u $SERVICE_NAME -f"
