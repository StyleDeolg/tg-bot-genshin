import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.api import auth, wheel, profile, referral, tasks, sponsors
from app.config import config  # 👈 ИСПОЛЬЗУЕМ config
from app.handlers import (
    start_command, help_command, profile_command,
    bind_uid_start, bind_uid_input, unbind_uid,
    app_command, donate_command, error_handler
)
from app.handlers.buttons import handle_buttons


# ========== LIFESPAN ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Запуск приложения...")
    
    if config.BOT_MODE != "polling":
        await set_webhook()
    
    print(f"✅ Бот запущен! Режим: {config.BOT_MODE}")
    print(f"📡 Webhook URL: {config.WEBHOOK_URL}")
    
    yield
    
    print("🛑 Остановка приложения...")


# ========== СОЗДАЕМ ПРИЛОЖЕНИЕ ==========
app = FastAPI(
    title="Genshin Bot API",
    version="0.1.0",
    lifespan=lifespan
)


# ========== ФУНКЦИЯ УСТАНОВКИ WEBHOOK ==========
async def set_webhook():
    """Устанавливает вебхук для бота при запуске"""
    if not config.WEBHOOK_URL:
        print("⚠️ WEBHOOK_URL не задан! Пропускаем установку вебхука.")
        return
    
    bot = Bot(token=config.BOT_TOKEN)
    
    try:
        await bot.set_webhook(
            url=config.WEBHOOK_URL,
            secret_token=config.WEBHOOK_SECRET_TOKEN,
            drop_pending_updates=True
        )
        print(f"✅ Webhook установлен: {config.WEBHOOK_URL}")
    except Exception as e:
        print(f"❌ Ошибка установки webhook: {e}")


# ========== CORS ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== API РОУТЕРЫ ==========
app.include_router(auth.router)
app.include_router(wheel.router)
app.include_router(profile.router)
app.include_router(referral.router)
app.include_router(tasks.router)
app.include_router(sponsors.router)


# ========== ФРОНТЕНД (SPA) ==========
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
    
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        if not path.startswith(("api", "webhook", "ping", "webhook-info")):
            file_path = os.path.join(FRONTEND_DIR, path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return FileResponse(file_path)
            return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# ========== ПРОВЕРКА РАБОТЫ ==========
@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "Backend is running!", "mode": config.BOT_MODE}


# ========== WEBHOOK ==========
TOKEN = config.BOT_TOKEN
WEBHOOK_PATH = "/webhook"
SECRET_TOKEN = config.WEBHOOK_SECRET_TOKEN

bot_app = Application.builder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("start", start_command))
bot_app.add_handler(CommandHandler("help", help_command))
bot_app.add_handler(CommandHandler("profile", profile_command))
bot_app.add_handler(CommandHandler("unbind_uid", unbind_uid))
bot_app.add_handler(CommandHandler("app", app_command))
bot_app.add_handler(CommandHandler("bind_uid", bind_uid_start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
bot_app.add_error_handler(error_handler)


@app.post(WEBHOOK_PATH)
async def webhook_endpoint(request: Request):
    if SECRET_TOKEN:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != SECRET_TOKEN:
            print(f"⚠️ Неверный секретный токен: {secret}")
            return Response(status_code=403)
    
    try:
        json_data = await request.json()
        update = Update.de_json(json_data, bot_app.bot)
        await bot_app.process_update(update)
        return Response(status_code=200)
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return Response(status_code=500)


@app.get("/webhook-info")
async def webhook_info():
    info = await bot_app.bot.get_webhook_info()
    return {
        "url": info.url,
        "pending_update_count": info.pending_update_count,
        "last_error_message": info.last_error_message,
    }