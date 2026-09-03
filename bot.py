# bot.py
import os
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет, мир!')

def main():
    # Замените 'YOUR_BOT_TOKEN' на токен вашего бота
    updater = Updater(token='YOUR_BOT_TOKEN', use_context=True)
    dp = updater.dispatcher

    # Добавляем обработчик для команды /start
    dp.add_handler(CommandHandler("start", start))

    # Запускаем бота
    updater.start_polling()

    # Обеспечиваем корректное завершение работы при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()