from telegram import Update
from telegram.ext import ContextTypes
from app.keyboards import get_keyboard_for_user
from app.config import ADMIN_IDS

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    text = update.message.text
    user = update.effective_user
    is_admin = user.id in ADMIN_IDS if user else False
    
    # --- ПРОВЕРКА: ЕСЛИ ЕСТЬ АКТИВНОЕ СОСТОЯНИЕ ДЛЯ UID ---
    # Если мы ждём ввод UID — передаём в bind_uid_input
    if context.user_data.get('waiting_for_uid', False):
        from app.handlers.bind_uid import bind_uid_input
        await bind_uid_input(update, context)
        return
    
    # --- КНОПКИ МЕНЮ ---
    if text == "👤 Профиль":
        from app.handlers.profile import profile_command
        await profile_command(update, context)
    
    elif text == "💎 Донаты":
        from app.handlers.donate import donate_command
        await donate_command(update, context)
    
    elif text == "🎮 Привязать UID":
        from app.handlers.bind_uid import bind_uid_start
        await bind_uid_start(update, context)
    
    elif text == "🔓 Отвязать UID":
        from app.handlers.unbind_uid import unbind_uid
        await unbind_uid(update, context)
    
    elif text == "📖 Помощь":
        from app.handlers.help import help_command
        await help_command(update, context)
    
    elif text == "👑 Админ-панель":
        if not is_admin:
            await update.message.reply_text("⛔ У вас нет прав.")
            return
        keyboard = get_keyboard_for_user(user.id)
        await update.message.reply_text(
            "👑 *Админ-панель*\n\n"
            "/add_sponsor — добавить спонсора\n"
            "/add_sponsor_task — добавить задание\n"
            "/list_sponsors — список спонсоров\n"
            "/add_referral_reward — награды за рефералов",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    else:
        keyboard = get_keyboard_for_user(user.id)
        await update.message.reply_text(
            "❌ Неизвестная команда. Используй кнопки внизу.",
            reply_markup=keyboard
        )