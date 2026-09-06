from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes

async def app_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    mini_app_url = "https://sleep-reorder-exception.ngrok-free.dev"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Открыть Mini App", web_app=WebAppInfo(url=mini_app_url))]
    ])

    await update.message.reply_text(
        "🎮 *Genshin Community Mini App*\n\n"
        "Нажми на кнопку ниже, чтобы открыть приложение.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )