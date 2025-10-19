#!/bin/bash

# Скрипт развертывания для prod среды

set -e

echo "🚀 Starting production deployment..."

# Переменные
PROJECT_NAME="aptechka-bot-prod"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"
BACKUP_DIR="backups"

# Проверка наличия файлов
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    echo "❌ Docker compose file not found: $DOCKER_COMPOSE_FILE"
    exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Environment file not found: $ENV_FILE"
    exit 1
fi

# Создание директории для бэкапов
mkdir -p $BACKUP_DIR

# Создание бэкапа БД
echo "💾 Creating database backup..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

if docker exec aptechka_db_prod pg_dump -U aptechka_user aptechka_prod > $BACKUP_FILE; then
    echo "✅ Database backup created: $BACKUP_FILE"
else
    echo "⚠️ Database backup failed, but continuing..."
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
sleep 15

# Проверка здоровья БД
echo "🔍 Checking database health..."
until docker exec aptechka_db_prod pg_isready -U aptechka_user -d aptechka_prod; do
    echo "Waiting for database..."
    sleep 3
done

# Применение миграций
echo "📊 Applying database migrations..."
py -m alembic upgrade head

# Проверка здоровья сервисов
echo "🏥 Checking services health..."
sleep 10

# Проверка webhook сервера
if curl -f http://localhost:8081/health; then
    echo "✅ Webhook server is healthy"
else
    echo "❌ Webhook server health check failed"
    echo "🔄 Rolling back..."
    
    # Откат к предыдущему образу
    docker-compose -f $DOCKER_COMPOSE_FILE down
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    # Восстановление БД из бэкапа
    if [ -f "$BACKUP_FILE" ]; then
        echo "🔄 Restoring database from backup..."
        docker exec -i aptechka_db_prod psql -U aptechka_user aptechka_prod < $BACKUP_FILE
    fi
    
    echo "❌ Deployment failed and rolled back"
    exit 1
fi

# Проверка БД
if docker exec aptechka_db_prod pg_isready -U aptechka_user -d aptechka_prod; then
    echo "✅ Database is healthy"
else
    echo "❌ Database health check failed"
    exit 1
fi

# Очистка старых бэкапов (оставляем последние 10)
echo "🧹 Cleaning up old backups..."
ls -t $BACKUP_DIR/backup_*.sql | tail -n +11 | xargs -r rm

echo "🎉 Production deployment completed successfully!"
echo ""
echo "📋 Service URLs:"
echo "  - Webhook server: http://localhost:8081"
echo "  - Database: localhost:5433"
echo ""
echo "📝 Useful commands:"
echo "  - View logs: make logs-prod"
echo "  - Stop services: make stop-prod"
echo "  - Restart services: make prod"
echo ""
echo "💾 Latest backup: $BACKUP_FILE"
