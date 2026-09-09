from telegram import Update
from telegram.ext import ContextTypes
from app.keyboards import get_main_keyboard, get_admin_keyboard
from app.config import config


async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки Донаты"""
    if not update.message:
        return
    
    user = update.effective_user
    is_admin = user.id in config.ADMIN_IDS if user else False
    keyboard = get_admin_keyboard() if is_admin else get_main_keyboard()
    
    donate_text = (
        "💎 *Поддержать проект*\n\n"
        "Если тебе нравится наш бот и ты хочешь помочь его развитию, "
        "ты можешь поддержать нас донатом.\n\n"
        "🚀 Способы поддержки:\n"
        "• USDT (TRC20): `TVk...`\n"
        "• Тинькофф: `+7 XXX XXX XX XX`\n"
        "• Boosty: https://boosty.to/...\n\n"
        "🙏 Спасибо, что ты с нами! ❤️"
    )
    
    await update.message.reply_text(
        donate_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )