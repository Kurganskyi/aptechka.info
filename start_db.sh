#!/bin/bash

# Запуск PostgreSQL в Docker
docker run -d \
  --name aptechka_postgres \
  -e POSTGRES_DB=aptechka \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine

echo "PostgreSQL запущен на порту 5432"
echo "Подключение: postgresql://postgres:postgres@localhost:5432/aptechka"
