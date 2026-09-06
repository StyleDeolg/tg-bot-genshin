from telegram import Update, ReplyKeyboardRemove, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.config import config
from app.keyboards import get_main_keyboard, get_admin_keyboard
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

TOKEN = config.BOT_TOKEN

def main():
    app = Application.builder().token(TOKEN).build()

    # --- Обычные команды ---
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("unbind_uid", unbind_uid))
    app.add_handler(CommandHandler("app", app_command))
    app.add_handler(CommandHandler("bind_uid", bind_uid_start))
    
    # --- Админ команды ---
    app.add_handler(CommandHandler("add_sponsor", add_sponsor))
    app.add_handler(CommandHandler("add_sponsor_task", add_sponsor_task))
    app.add_handler(CommandHandler("list_sponsors", list_sponsors))
    app.add_handler(CommandHandler("add_referral_reward", add_referral_reward))

    # --- ОБРАБОТЧИК ВСЕХ ТЕКСТОВЫХ СООБЩЕНИЙ (ОДИН!) ---
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    # --- Обработчик ошибок ---
    app.add_error_handler(error_handler)

    print("🤖 Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()