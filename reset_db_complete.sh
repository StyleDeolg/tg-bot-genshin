#!/bin/bash

echo "========================================"
echo " ПОЛНАЯ ОЧИСТКА БД"
echo "========================================"

echo ""
echo "[1/7] Останавливаем контейнеры..."
docker-compose down -v

echo ""
echo "[2/7] Запускаем PostgreSQL..."
docker-compose up -d postgres
sleep 5

echo ""
echo "[3/7] Создаём базу данных..."
docker exec -it genshin_postgres psql -U genshin_user -d postgres -c "DROP DATABASE IF EXISTS genshin_db;"
docker exec -it genshin_postgres psql -U genshin_user -d postgres -c "CREATE DATABASE genshin_db;"

echo ""
echo "[4/7] Удаляем старые миграции..."
cd alembic/versions || exit
rm -f *.py
echo "" > __init__.py
cd ../..

echo ""
echo "[5/7] Создаём новые миграции..."
alembic revision --autogenerate -m "initial_migration"
alembic upgrade head

echo ""
echo "[6/7] Добавляем призы..."
python add_prizes.py

echo ""
echo "[7/7] Добавляем данные..."
python add_referral_rewards.py
python add_tasks.py

echo ""
echo "========================================"
echo " ГОТОВО!"
echo " БД полностью пересоздана."
echo "========================================"
read -p "Нажмите Enter для выхода..."