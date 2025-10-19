# Развертывание Aptechka Bot

## Подготовка сервера

### 1. Установка зависимостей

```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Устанавливаем Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Устанавливаем Nginx
sudo apt install nginx -y

# Устанавливаем certbot для SSL
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Настройка домена и SSL

```bash
# Настройте DNS для вашего домена
# Затем получите SSL сертификат
sudo certbot --nginx -d your-domain.com

# Обновите nginx.conf с вашим доменом
sudo cp deploy/nginx.conf /etc/nginx/sites-available/aptechka-bot
sudo ln -s /etc/nginx/sites-available/aptechka-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Настройка переменных окружения

```bash
# Создайте директорию проекта
sudo mkdir -p /opt/aptechka-bot
sudo chown $USER:$USER /opt/aptechka-bot

# Скопируйте файлы проекта
cp -r . /opt/aptechka-bot/

# Создайте .env файл
cd develop/opt/aptechka-bot
cp .env.example .env

# Отредактируйте .env файл с вашими настройками
nano .env
```

### 4. Настройка systemd сервиса

```bash
# Скопируйте service файл
sudo cp deploy/aptechka-bot.service /etc/systemd/system/

# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск
sudo systemctl enable aptechka-bot
```

## Переменные окружения

### Обязательные переменные:

```bash
# Telegram Bot
BOT_TOKEN=your_bot_token_here
WEBHOOK_HOST=https://your-domain.com
WEBHOOK_PATH=/webhook/bepaid
WEBHOOK_PORT=8080

# База данных
DATABASE_URL=postgresql://user:password@localhost:5432/aptechka

# bePaid
BEPAID_SHOP_ID=your_shop_id
BEPAID_SECRET_KEY=your_secret_key

# Админы
ADMIN_IDS=123456789,987654321

# Логирование
LOG_LEVEL=INFO
```

### Для разработки добавьте:

```bash
# Разработка
ENVIRONMENT=development
DEBUG=true
```

## Развертывание

### Автоматическое развертывание (через GitHub Actions)

1. Настройте secrets в GitHub:
   - `DEV_BOT_TOKEN` - токен бота для dev
   - `PROD_BOT_TOKEN` - токен бота для prod
   - `DEV_HOST`, `DEV_USER`, `DEV_SSH_KEY` - данные dev сервера
   - `PROD_HOST`, `PROD_USER`, `PROD_SSH_KEY` - данные prod сервера

2. Push в соответствующие ветки:
   - `develop` → автоматический деплой на dev
   - `main` → автоматический деплой на prod

### Ручное развертывание

```bash
# Сделайте скрипт исполняемым
chmod +x deploy/deploy.sh

# Развертывание на dev
./deploy/deploy.sh dev

# Развертывание на prod
./deploy/deploy.sh prod
```

## Мониторинг и логи

### Просмотр логов

```bash
# Логи systemd сервиса
sudo journalctl -u aptechka-bot -f

# Логи Docker контейнеров
docker-compose -f docker-compose.prod.yml logs -f

# Логи Nginx
sudo tail -f /var/log/nginx/aptechka_bot_access.log
sudo tail -f /var/log/nginx/aptechka_bot_error.log
```

### Проверка статуса

```bash
# Статус сервиса
sudo systemctl status aptechka-bot

# Статус контейнеров
docker-compose -f docker-compose.prod.yml ps

# Проверка здоровья
curl -f http://localhost:8080/health || echo "Service is down"
```

## Обслуживание

### Обновление

```bash
cd /opt/aptechka-bot
git pull origin main
./deploy/deploy.sh prod
```

### Резервное копирование БД

```bash
# Создание бэкапа
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres aptechka > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из бэкапа
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres aptechka < backup_file.sql
```

### Очистка логов

```bash
# Очистка логов Docker
docker system prune -f

# Ротация логов systemd
sudo journalctl --vacuum-time=7d

# Очистка логов Nginx
sudo logrotate /etc/logrotate.d/nginx
```

## Безопасность

1. **Firewall**: Настройте UFW или iptables
2. **SSH**: Используйте ключи вместо паролей
3. **Updates**: Регулярно обновляйте систему
4. **Monitoring**: Настройте мониторинг сервисов
5. **Backups**: Регулярно создавайте резервные копии

## Troubleshooting

### Бот не отвечает

```bash
# Проверьте статус
sudo systemctl status aptechka-bot

# Проверьте логи
sudo journalctl -u aptechka-bot -n 50

# Перезапустите сервис
sudo systemctl restart aptechka-bot
```

### Проблемы с БД

```bash
# Проверьте подключение к БД
docker-compose -f docker-compose.prod.yml exec bot python -c "import psycopg2; print('DB OK')"

# Запустите миграции
docker-compose -f docker-compose.prod.yml exec bot alembic upgrade head
```

### Проблемы с webhook

```bash
# Проверьте Nginx
sudo nginx -t
sudo systemctl status nginx

# Проверьте доступность webhook
curl -f https://your-domain.com/webhook/bepaid
```
