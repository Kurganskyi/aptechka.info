#!/bin/bash

# Остановка бота
echo "Остановка бота..."

# Поиск и завершение процесса бота
pkill -f "python.*simple_bot.py"
pkill -f "python.*run_bot.py"
pkill -f "python.*src.main"

echo "Бот остановлен"
