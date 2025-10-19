# 🐧 Настройка WSL для разработки

## После перезагрузки системы

После установки Ubuntu через `wsl --install Ubuntu` система требует перезагрузки. После перезагрузки:

### 1. Запуск WSL
```bash
wsl
```

### 2. Первоначальная настройка Ubuntu
При первом запуске Ubuntu попросит создать пользователя и пароль.

### 3. Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

### 4. Установка необходимых пакетов
```bash
# Python и pip
sudo apt install python3 python3-pip python3-venv -y

# Git
sudo apt install git -y

# Docker (опционально)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Make
sudo apt install make -y
```

### 5. Переход в директорию проекта
```bash
cd /mnt/c/Users/kurga/Desktop/aptechka.info
```

### 6. Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate
```

### 7. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 8. Настройка переменных окружения
```bash
cp env.example .env
nano .env  # Отредактируйте файл с вашими настройками
```

### 9. Запуск базы данных
```bash
make dev
```

### 10. Применение миграций
```bash
make migrate-up
```

### 11. Запуск бота
```bash
make run
```

## 🚀 Альтернативный способ (с Docker)

Если предпочитаете Docker:

```bash
# Запуск всех сервисов
docker-compose -f docker-compose.dev.yml up -d

# Применение миграций
docker-compose -f docker-compose.dev.yml exec bot alembic upgrade head

# Просмотр логов
docker-compose -f docker-compose.dev.yml logs -f bot
```

## 📁 Структура в WSL

В WSL ваш проект будет доступен по пути:
```
/mnt/c/Users/kurga/Desktop/aptechka.info
```

## 🔧 Полезные команды

```bash
# Активация виртуального окружения
source venv/bin/activate

# Деактивация виртуального окружения
deactivate

# Просмотр статуса Git
git status

# Создание коммита
git add .
git commit -m "Описание изменений"
git push origin develop
```

## 🐛 Решение проблем

### Проблемы с правами доступа
```bash
# Если возникают проблемы с правами на файлы
sudo chown -R $USER:$USER /mnt/c/Users/kurga/Desktop/aptechka.info
```

### Проблемы с Docker в WSL
```bash
# Перезапуск Docker daemon
sudo service docker restart

# Проверка статуса
sudo service docker status
```

### Проблемы с Python путями
```bash
# Добавление текущей директории в PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## 📚 Дополнительные ресурсы

- [Документация WSL](https://docs.microsoft.com/en-us/windows/wsl/)
- [Docker в WSL](https://docs.docker.com/desktop/wsl/)
- [Git в WSL](https://docs.github.com/en/github/getting-started-with-github/quickstart)

## ✅ Проверка установки

После настройки проверьте:

```bash
# Python
python3 --version

# Pip
pip --version

# Git
git --version

# Docker (если установлен)
docker --version

# Make
make --version
```

Все команды должны работать без ошибок!
