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
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatJoinRequestHandler,
    filters,
    ContextTypes,
)
from app.handlers import (
    start_command, help_command, profile_command,
    bind_uid_start, unbind_uid, app_command, donate_command, error_handler
)
from app.handlers.buttons import handle_buttons
from app.handlers.join_request import handle_join_request

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
        _bot_app.add_handler(CommandHandler("bind_uid", bind_uid_start))
        
        # 🔥 НОВОЕ: обработчик заявок на вступление в каналы
        _bot_app.add_handler(ChatJoinRequestHandler(handle_join_request))
        
        # Обработчик всех текстовых сообщений (кнопки и ввод)
        _bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
        _bot_app.add_error_handler(error_handler)
        
        await _bot_app.initialize()
        print("✅ Бот инициализирован")
        
        # 🔥 ВАЖНО: подписываемся на chat_join_request в вебхуке
        # Если WEBHOOK_URL задан — устанавливаем вебхук с нужными allowed_updates
        webhook_url = getattr(config, "WEBHOOK_URL", None)
        if webhook_url:
            full_url = f"{webhook_url.rstrip('/')}{WEBHOOK_PATH}"
            try:
                await _bot_app.bot.set_webhook(
                    url=full_url,
                    secret_token=SECRET_TOKEN if SECRET_TOKEN else None,
                    allowed_updates=[
                        "message",
                        "callback_query",
                        "chat_join_request",
                    ],
                )
                print(f"✅ Вебхук установлен: {full_url}")
            except Exception as e:
                print(f"❌ Не удалось установить вебхук: {e}")
        else:
            print("⚠️ WEBHOOK_URL не задан в config — пропускаю установку вебхука")

    return _bot_app


@app.post(WEBHOOK_PATH)
async def webhook_endpoint(request: Request):
    if SECRET_TOKEN:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != SECRET_TOKEN:
            return Response(status_code=403)
    try:
        print("🔍 [webhook] Получен запрос")
        bot_app = await get_bot_app()
        json_data = await request.json()
        
        # Логируем тип апдейта
        update_type = list(json_data.keys())
        print(f"🔍 [webhook] Тип апдейта: {update_type}")
        
        update = Update.de_json(json_data, bot_app.bot)
        await bot_app.process_update(update)
        print("🔍 [webhook] Обработка завершена")
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
            "allowed_updates": info.allowed_updates,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/set-webhook")
async def set_webhook_manually():
    """Ручная установка вебхука с нужными allowed_updates."""
    try:
        bot_app = await get_bot_app()
        webhook_url = getattr(config, "WEBHOOK_URL", None)
        if not webhook_url:
            return {"error": "WEBHOOK_URL не задан в config"}
        full_url = f"{webhook_url.rstrip('/')}{WEBHOOK_PATH}"
        await bot_app.bot.set_webhook(
            url=full_url,
            secret_token=SECRET_TOKEN if SECRET_TOKEN else None,
            allowed_updates=["message", "callback_query", "chat_join_request"],
        )
        info = await bot_app.bot.get_webhook_info()
        return {
            "success": True,
            "url": info.url,
            "allowed_updates": info.allowed_updates,
        }
    except Exception as e:
        return {"error": str(e)}


print("🚀 Бот запущен!")