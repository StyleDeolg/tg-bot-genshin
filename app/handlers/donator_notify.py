from telegram import Bot
from app.config import config

BOT_TOKEN = config.BOT_TOKEN
bot = Bot(token=BOT_TOKEN)

async def notify_donator(winner_telegram_id: int, prize: str, uid: str, server: str, username: str):
    """Отправляет уведомление донатчику"""
    text = (
        f"🎁 *Новый донат!*\n\n"
        f"👤 Победитель: @{username or 'Unknown'}\n"
        f"🆔 UID: `{uid}`\n"
        f"🌍 Регион: {server}\n"
        f"🏆 Выигрыш: {prize}\n\n"
        f"Пожалуйста, свяжитесь с победителем и совершите донат!"
    )
    
    # TODO: Заменить на ID донатчика
    DONATOR_CHAT_ID = 5646848256  # Твой ID или ID донатчика
    
    try:
        await bot.send_message(
            chat_id=DONATOR_CHAT_ID,
            text=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления донатчику: {e}")