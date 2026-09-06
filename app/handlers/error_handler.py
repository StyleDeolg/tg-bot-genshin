import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")
    
    # Безопасно проверяем, есть ли сообщение
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text("❌ Произошла ошибка. Попробуйте позже.")