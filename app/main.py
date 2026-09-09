import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, wheel, profile, referral, tasks, sponsors
from app.config import config

app = FastAPI(title="Genshin Bot API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(auth.router)
app.include_router(wheel.router)
app.include_router(profile.router)
app.include_router(referral.router)
app.include_router(tasks.router)
app.include_router(sponsors.router)

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "Backend is running!"}

# ========== WEBHOOK ==========
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.handlers import (
    start_command, help_command, profile_command,
    bind_uid_start, unbind_uid, app_command, donate_command, error_handler
)
from app.handlers.buttons import handle_buttons

TOKEN = config.BOT_TOKEN
WEBHOOK_PATH = "/webhook"
SECRET_TOKEN = config.WEBHOOK_SECRET_TOKEN

# Глобальная переменная для бота
_bot_app = None

async def get_bot_app():
    global _bot_app
    if _bot_app is None:
        _bot_app = Application.builder().token(TOKEN).build()
        _bot_app.add_handler(CommandHandler("start", start_command))
        _bot_app.add_handler(CommandHandler("help", help_command))
        _bot_app.add_handler(CommandHandler("profile", profile_command))
        _bot_app.add_handler(CommandHandler("unbind_uid", unbind_uid))
        _bot_app.add_handler(CommandHandler("app", app_command))
        _bot_app.add_handler(CommandHandler("bind_uid", bind_uid_start))
        _bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
        _bot_app.add_error_handler(error_handler)
        
        # 👇 ЯВНАЯ ИНИЦИАЛИЗАЦИЯ
        await _bot_app.initialize()
        print("✅ Бот инициализирован")
    return _bot_app

@app.post(WEBHOOK_PATH)
async def webhook_endpoint(request: Request):
    if SECRET_TOKEN:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != SECRET_TOKEN:
            return Response(status_code=403)
    try:
        bot_app = await get_bot_app()
        json_data = await request.json()
        update = Update.de_json(json_data, bot_app.bot)
        await bot_app.process_update(update)
        return Response(status_code=200)
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return Response(status_code=500)

@app.get("/webhook-info")
async def webhook_info():
    try:
        bot_app = await get_bot_app()
        info = await bot_app.bot.get_webhook_info()
        return {
            "url": info.url,
            "pending_update_count": info.pending_update_count,
            "last_error_message": info.last_error_message,
        }
    except Exception as e:
        return {"error": str(e)}

print("🚀 Бот запущен!")