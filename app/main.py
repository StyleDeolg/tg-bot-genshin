import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, wheel, profile, referral, tasks, sponsors
from app.config import config

app = FastAPI(title="Genshin Bot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(wheel.router)
app.include_router(profile.router)
app.include_router(referral.router)
app.include_router(tasks.router)
app.include_router(sponsors.router)


@app.get("/ping")
async def ping():
    return {
        "status": "ok",
        "message": "Backend is running!",
        "mode": config.BOT_MODE,
        "admins": config.ADMIN_IDS,
        "donators": config.DONATOR_CHAT_IDS
    }


# ========== WEBHOOK ==========
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from app.handlers import (
    start_command, help_command, profile_command,
    bind_uid_start, unbind_uid, app_command, donate_command, error_handler
)
from app.handlers.buttons import handle_buttons
from app.handlers.bind_uid import bind_uid_input, bind_uid_server, WAITING_UID, WAITING_SERVER

TOKEN = config.BOT_TOKEN
WEBHOOK_PATH = "/webhook"
SECRET_TOKEN = config.WEBHOOK_SECRET_TOKEN

_bot_app = None

async def get_bot_app():
    global _bot_app
    if _bot_app is None:
        _bot_app = Application.builder().token(TOKEN).build()
        
        # Команды
        _bot_app.add_handler(CommandHandler("start", start_command))
        _bot_app.add_handler(CommandHandler("help", help_command))
        _bot_app.add_handler(CommandHandler("profile", profile_command))
        _bot_app.add_handler(CommandHandler("unbind_uid", unbind_uid))
        _bot_app.add_handler(CommandHandler("app", app_command))
        
        # ===== CONVERSATION HANDLER (ДОЛЖЕН БЫТЬ ВЫШЕ MessageHandler) =====
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("bind_uid", bind_uid_start)],
            states={
                WAITING_UID: [MessageHandler(filters.TEXT & ~filters.COMMAND, bind_uid_input)],
                WAITING_SERVER: [MessageHandler(filters.TEXT & ~filters.COMMAND, bind_uid_server)],
            },
            fallbacks=[CommandHandler("start", start_command)],
        )
        _bot_app.add_handler(conv_handler)
        
        # ===== ОБРАБОТЧИК КНОПОК (ДОЛЖЕН БЫТЬ НИЖЕ) =====
        _bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
        _bot_app.add_error_handler(error_handler)
        
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