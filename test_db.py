import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="genshin_db",
        user="genshin_user",
        password="genshin_pass"
    )
    print("✅ Подключение к PostgreSQL успешно!")
    conn.close()
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")