from telegram import Update
from telegram.ext import ContextTypes
from app.keyboards import get_keyboard_for_user

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.effective_user
    keyboard = get_keyboard_for_user(user.id)

    help_text = (
        "📖 *Справка по командам:*\n\n"
        "👤 Профиль — посмотреть свой профиль\n"
        "💎 Донаты — поддержать проект\n"
        "🎮 Привязать UID — привязать Genshin UID\n"
        "🔓 Отвязать UID — отвязать Genshin UID\n"
        "📖 Помощь — показать эту справку\n\n"
        "❓ По вопросам пишите в поддержку: @support"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=keyboard)