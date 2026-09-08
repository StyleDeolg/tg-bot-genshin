from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, wheel, profile, referral, tasks
import os  # ← ДОБАВИТЬ

# --- ИМПОРТЫ ДЛЯ WEBHOOK ---
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.config import config
from app.handlers import (
    start_command,
    help_command,
    profile_command,
    bind_uid_start,
    bind_uid_input,
    unbind_uid,
    app_command,
    donate_command,
    add_sponsor,
    add_sponsor_task,
    list_sponsors,
    add_referral_reward,
    error_handler
)
from app.handlers.buttons import handle_buttons

app = FastAPI(title="Genshin Bot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры
app.include_router(auth.router)
app.include_router(wheel.router)
app.include_router(profile.router)
app.include_router(referral.router)
app.include_router(tasks.router)

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "Backend is running on Python 3.14!"}

# ========== WEBHOOK ДЛЯ БОТА ==========
TOKEN = config.BOT_TOKEN
WEBHOOK_PATH = "/webhook"
SECRET_TOKEN = os.getenv("WEBHOOK_SECRET_TOKEN", "your-secret-token-here")

# Создаем приложение бота
bot_app = Application.builder().token(TOKEN).build()

# Регистрируем все хендлеры
bot_app.add_handler(CommandHandler("start", start_command))
bot_app.add_handler(CommandHandler("help", help_command))
bot_app.add_handler(CommandHandler("profile", profile_command))
bot_app.add_handler(CommandHandler("unbind_uid", unbind_uid))
bot_app.add_handler(CommandHandler("app", app_command))
bot_app.add_handler(CommandHandler("bind_uid", bind_uid_start))
bot_app.add_handler(CommandHandler("add_sponsor", add_sponsor))
bot_app.add_handler(CommandHandler("add_sponsor_task", add_sponsor_task))
bot_app.add_handler(CommandHandler("list_sponsors", list_sponsors))
bot_app.add_handler(CommandHandler("add_referral_reward", add_referral_reward))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
bot_app.add_error_handler(error_handler)

@app.post(WEBHOOK_PATH)
async def webhook_endpoint(request: Request):
    """
    Обрабатывает входящие обновления от Telegram через webhook.
    """
    # Проверяем секретный токен (для безопасности)
    if os.getenv("BOT_MODE") == "webhook":
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != SECRET_TOKEN:
            return Response(status_code=403)
    
    try:
        json_data = await request.json()
        update = Update.de_json(json_data, bot_app.bot)
        await bot_app.process_update(update)
        return Response(status_code=200)
    except Exception as e:
        print(f"❌ Ошибка в webhook: {e}")
        return Response(status_code=500)

@app.get("/webhook-info")
async def webhook_info():
    """Проверка статуса webhook"""
    info = await bot_app.bot.get_webhook_info()
    return {
        "url": info.url,
        "pending_update_count": info.pending_update_count,
        "last_error_message": info.last_error_message,
    }