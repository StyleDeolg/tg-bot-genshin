from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from app.config import config
from app.handlers import (
    start_command,
    help_command,
    profile_command,
    bind_uid_start,
    bind_uid_input,
    unbind_uid,
    app_command,
    error_handler,
    admin_panel,
    admin_exit,
)
from app.handlers.buttons import handle_buttons
from app.handlers.admin import (
    admin_stats,
    admin_prizes,
    admin_tasks,
    admin_give_tickets_start,
    admin_give_tickets_process,
    admin_broadcast_start,
    admin_broadcast_process,
    admin_give_moon,
    admin_give_moon_user,
)
from app.handlers.sponsors import (
    add_sponsor_start,
    add_sponsor_name,
    add_sponsor_link,
    add_sponsor_channel_id,  # ← ИСПРАВЛЕНО (было add_sponsor_forward)
    delete_sponsor_start,
    delete_sponsor_confirm,
    list_sponsors_admin,
)

TOKEN = config.BOT_TOKEN

# Состояния для ConversationHandler
ADD_SPONSOR_NAME, ADD_SPONSOR_LINK, ADD_SPONSOR_CHANNEL_ID = 1, 2, 3  # ← ИСПРАВЛЕНО
GIVE_TICKETS_USER = 4
SEND_BROADCAST = 5
GIVE_MOON_USER = 6

def main():
    app = Application.builder().token(TOKEN).build()

    # --- Обычные команды ---
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("unbind_uid", unbind_uid))
    app.add_handler(CommandHandler("app", app_command))
    app.add_handler(CommandHandler("bind_uid", bind_uid_start))
    
    # --- Админ-команды ---
    app.add_handler(CommandHandler("admin", admin_panel))

    # --- ConversationHandler для добавления спонсора ---
    add_sponsor_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^➕ Добавить спонсора$"), add_sponsor_start)],
        states={
            ADD_SPONSOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_sponsor_name)],
            ADD_SPONSOR_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_sponsor_link)],
            ADD_SPONSOR_CHANNEL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_sponsor_channel_id)],
        },
        fallbacks=[CommandHandler("admin", admin_panel)],
    )
    app.add_handler(add_sponsor_conv)

    # --- ConversationHandler для выдачи билетов ---
    give_tickets_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎫 Выдать билеты$"), admin_give_tickets_start)],
        states={
            GIVE_TICKETS_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_give_tickets_process)],
        },
        fallbacks=[
            CommandHandler("admin", admin_panel),
            MessageHandler(filters.Regex("^🔙 Выйти из админки$"), admin_exit),
        ],
    )
    app.add_handler(give_tickets_conv)

    # --- ConversationHandler для рассылки ---
    broadcast_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📢 Рассылка$"), admin_broadcast_start)],
        states={
            SEND_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_broadcast_process)],
        },
        fallbacks=[
            CommandHandler("admin", admin_panel),
            MessageHandler(filters.Regex("^🔙 Выйти из админки$"), admin_exit),
        ],
    )
    app.add_handler(broadcast_conv)

    # --- ConversationHandler для выдачи луны ---
    give_moon_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🌙 Выдать луну$"), admin_give_moon)],
        states={
            GIVE_MOON_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_give_moon_user)],
        },
        fallbacks=[
            CommandHandler("admin", admin_panel),
            MessageHandler(filters.Regex("^🔙 Выйти из админки$"), admin_exit),
        ],
    )
    app.add_handler(give_moon_conv)

    # --- Обработчик всех текстовых сообщений ---
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    # --- Обработчик ошибок ---
    app.add_error_handler(error_handler)

    print("🤖 Бот запущен...")
    print("📌 Напиши /admin для открытия админ-панели")
    app.run_polling()

if __name__ == "__main__":
    main()