# Makefile для управления проектом

.PHONY: help install dev prod test lint format clean migrate

# Переменные
PYTHON := py
DOCKER_COMPOSE_DEV := docker-compose -f docker-compose.dev.yml
DOCKER_COMPOSE_PROD := docker-compose -f docker-compose.prod.yml

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -r requirements-dev.txt

dev: ## Запустить dev среду
	$(DOCKER_COMPOSE_DEV) up -d
	$(PYTHON) -m alembic upgrade head
	$(PYTHON) -m src.main

prod: ## Запустить prod среду
	$(DOCKER_COMPOSE_PROD) up -d
	$(PYTHON) -m alembic upgrade head
	$(PYTHON) -m src.main

test: ## Запустить тесты
	$(PYTHON) -m pytest tests/ -v --cov=src

lint: ## Проверить код линтерами
	$(PYTHON) -m ruff check src/
	$(PYTHON) -m mypy src/

format: ## Форматировать код
	$(PYTHON) -m black src/ tests/
	$(PYTHON) -m ruff check --fix src/

clean: ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

migrate: ## Создать новую миграцию
	$(PYTHON) -m alembic revision --autogenerate -m "$(msg)"

migrate-up: ## Применить миграции
	$(PYTHON) -m alembic upgrade head

migrate-down: ## Откатить последнюю миграцию
	$(PYTHON) -m alembic downgrade -1

db-reset: ## Сбросить БД (осторожно!)
	$(DOCKER_COMPOSE_DEV) down -v
	$(DOCKER_COMPOSE_DEV) up -d
	sleep 5
	$(PYTHON) -m alembic upgrade head

logs-dev: ## Показать логи dev среды
	$(DOCKER_COMPOSE_DEV) logs -f

logs-prod: ## Показать логи prod среды
	$(DOCKER_COMPOSE_PROD) logs -f

stop-dev: ## Остановить dev среду
	$(DOCKER_COMPOSE_DEV) down

stop-prod: ## Остановить prod среду
	$(DOCKER_COMPOSE_PROD) down

backup-db: ## Создать бэкап БД
	@echo "Создание бэкапа БД..."
	@mkdir -p backups
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	docker exec aptechka_db_prod pg_dump -U aptechka_user aptechka_prod > backups/backup_$$timestamp.sql

restore-db: ## Восстановить БД из бэкапа (использовать: make restore-db file=backup_file.sql)
	@if [ -z "$(file)" ]; then echo "Использование: make restore-db file=backup_file.sql"; exit 1; fi
	@echo "Восстановление БД из $(file)..."
	@docker exec -i aptechka_db_prod psql -U aptechka_user aptechka_prod < $(file)

health-check: ## Проверить здоровье сервисов
	@echo "Проверка health check..."
	@curl -f http://localhost:8080/health || echo "Webhook server недоступен"
	@docker exec aptechka_db_dev pg_isready -U aptechka_user -d aptechka_dev || echo "БД недоступна"
