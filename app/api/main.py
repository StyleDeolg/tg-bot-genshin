from fastapi import FastAPI
from app.api import auth, wheel
from app.config import config

app = FastAPI(title="Genshin Bot API", version="0.1.0")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(wheel.router)  # <-- ДОБАВЛЯЕМ

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "Backend is running on Python 3.14!"}