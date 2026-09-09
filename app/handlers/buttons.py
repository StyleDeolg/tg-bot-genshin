from telegram import Update
from telegram.ext import ContextTypes
from app.keyboards import get_keyboard_for_user
from app.handlers.start import start_command
from app.handlers.profile import profile_command
from app.handlers.bind_uid import bind_uid_start
from app.handlers.unbind_uid import unbind_uid
from app.handlers.help import help_command
from app.handlers.admin import (
    admin_panel,
    admin_exit,
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
    delete_sponsor_start,
    delete_sponsor_confirm,
    list_sponsors_admin,
    add_sponsor_start,
)
from app.config import config


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопок.
    Этот обработчик НЕ получает сообщения, когда активен диалог bind_uid,
    потому что мы добавили фильтр в main.py
    """
    
    text = update.message.text
    user_id = update.effective_user.id
    
    # ===== АКТИВНЫЕ ДЕЙСТВИЯ АДМИНКИ =====
    action = context.user_data.get('admin_action')
    
    if action == 'give_tickets':
        await admin_give_tickets_process(update, context)
        return
    
    if action == 'broadcast':
        await admin_broadcast_process(update, context)
        return
    
    if action == 'delete_sponsor':
        await delete_sponsor_confirm(update, context)
        return
    
    if action == 'give_moon':
        await admin_give_moon_user(update, context)
        return
    
    # ===== ОБЫЧНЫЕ КНОПКИ =====
    if text == "👤 Профиль":
        await profile_command(update, context)
    elif text == "🎮 Привязать UID":
        await bind_uid_start(update, context)
    elif text == "🔓 Отвязать UID":
        await unbind_uid(update, context)
    elif text == "📖 Помощь":
        await help_command(update, context)
    
    # ===== АДМИН-КНОПКИ =====
    elif text == "👑 Админ-панель":
        if user_id in config.ADMIN_IDS:
            await admin_panel(update, context)
        else:
            await update.message.reply_text("⛔ У вас нет доступа к админ-панели")
    
    elif text == "📊 Статистика":
        if user_id in config.ADMIN_IDS:
            await admin_stats(update, context)
        else:
            await update.message.reply_text("⛔ Нет доступа")
    
    elif text == "🎡 Призы":
        if user_id in config.ADMIN_IDS:
            await admin_prizes(update, context)
        else:
            await update.message.reply_text("⛔ Нет доступа")
    
    elif text == "📋 Задания":
        if user_id in config.ADMIN_IDS:
            await admin_tasks(update, context)
        else:
            await update.message.reply_text("⛔ Нет доступа")
    
    elif text == "🎫 Выдать билеты":
        if user_id in config.ADMIN_IDS:
            await admin_give_tickets_start(update, context)
        else:
            await update.message.reply_text("⛔ Нет доступа")
    
    elif text == "📢 Рассылка":
        if user_id in config.ADMIN_IDS:
            await admin_broadcast_start(update, context)
        else:
            await update.message.reply_text("⛔ Нет доступа")
    
    elif text == "🌙 Выдать луну":
        if user_id in config.ADMIN_IDS:
            await admin_give_moon(update, context)
        else:
            await update.message.reply_text("⛔ Нет доступа")
    
    elif text == "➕ Добавить спонсора":
        if user_id in config.ADMIN_IDS:
            await add_sponsor_start(update, context)
        else:
            await update.message.reply_text("⛔ Нет доступа")
    
    elif text == "🗑 Удалить спонсора":
        if user_id in config.ADMIN_IDS:
            await delete_sponsor_start(update, context)
        else:
            await update.message.reply_text("⛔ Нет доступа")
    
    elif text == "📋 Список спонсоров":
        if user_id in config.ADMIN_IDS:
            await list_sponsors_admin(update, context)
        else:
            await update.message.reply_text("⛔ Нет доступа")
    
    elif text == "🔙 Выйти из админки":
        if user_id in config.ADMIN_IDS:
            await admin_exit(update, context)
        else:
            await update.message.reply_text("⛔ Нет доступа")
    
    else:
        await update.message.reply_text(
            "❌ Неизвестная команда. Используйте кнопки меню.",
            reply_markup=get_keyboard_for_user(user_id)
        )