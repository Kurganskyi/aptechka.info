# Aptechka Bot

Telegram бот для продажи аптечек первой помощи с интеграцией bePaid.

## 🏗️ Архитектура

Проект построен на принципах Clean Architecture:

- **Domain Layer** - бизнес-логика и сущности
- **Infrastructure Layer** - работа с БД, внешними API  
- **Presentation Layer** - handlers, keyboards, middlewares

## 🛠️ Технологии

- **Python 3.11+** - основной язык
- **aiogram 3.x** - Telegram Bot API
- **PostgreSQL** - база данных
- **SQLAlchemy + Alembic** - ORM и миграции
- **bePaid API** - платежная система
- **Docker + Docker Compose** - контейнеризация
- **GitHub Actions** - CI/CD
- **Nginx** - reverse proxy
- **systemd** - управление сервисами

## 🚀 Быстрый старт

### Локальная разработка

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd aptechka.info

# 2. Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env файл

# 3. Установите зависимости
make install

# 4. Запустите БД
make dev

# 5. Выполните миграции
make migrate-up

# 6. Запустите бота
make run
```

### Продакшн развертывание

```bash
# Смотрите подробные инструкции в deploy/README.md
./deploy/deploy.sh prod
```

## 📋 Команды разработки

```bash
make install          # Установка зависимостей
make dev              # Запуск в dev режиме
make lint             # Проверка кода
make test             # Запуск тестов
make migrate-up       # Применение миграций
make migrate-down     # Откат миграций
make build-dev        # Сборка dev образа
make build-prod       # Сборка prod образа
make deploy-dev       # Деплой на dev
make deploy-prod      # Деплой на prod
```

## 🎯 Функциональность

### Основные возможности:
- ✅ Регистрация пользователей
- ✅ Каталог аптечек с описаниями
- ✅ Интеграция с bePaid для оплаты
- ✅ Система тестирования (6 вопросов)
- ✅ FAQ с пользовательскими вопросами
- ✅ Доставка файлов после оплаты
- ✅ Админ-панель для управления

### Продукты:
- 🎥 Трипвайер за 1 BYN
- 🎥 Трипвайер за 99 BYN  
- 📖 Гайд за 1 BYN
- 📦 Аптечки разных категорий

## 🔧 Конфигурация

### Обязательные переменные:

```bash
# Telegram Bot
BOT_TOKEN=your_bot_token
WEBHOOK_HOST=https://your-domain.com
WEBHOOK_PORT=8080

# База данных  
DATABASE_URL=postgresql://user:pass@localhost:5432/aptechka

# bePaid
BEPAID_SHOP_ID=your_shop_id
BEPAID_SECRET_KEY=your_secret_key

# Админы
ADMIN_IDS=123456789,987654321
```

## 📊 Мониторинг

### Логи:
```bash
# Логи сервиса
sudo journalctl -u aptechka-bot -f

# Логи контейнеров
docker-compose logs -f

# Логи Nginx
sudo tail -f /var/log/nginx/aptechka_bot_*.log
```

### Health Check:
```bash
curl -f http://localhost:8080/health
```

## 🛡️ Безопасность

- ✅ SSL/TLS шифрование
- ✅ Rate limiting
- ✅ IP whitelist для webhooks
- ✅ Валидация подписей bePaid
- ✅ Блокировка пользователей
- ✅ Логирование всех действий

## 📈 CI/CD

- **develop** → автоматический деплой на dev сервер
- **main** → автоматический деплой на prod сервер
- Автоматические тесты и проверки
- Security scanning
- Blue-green deployment

## 🤝 Разработка

1. Создайте feature ветку от `develop`
2. Внесите изменения
3. Создайте Pull Request
4. После ревью и тестов - merge в `develop`
5. Для релиза - merge `develop` в `main`

## 📞 Поддержка

Для вопросов по развертыванию см. [deploy/README.md](deploy/README.md)

## 📄 Лицензия

Проект создан для коммерческого использования.
