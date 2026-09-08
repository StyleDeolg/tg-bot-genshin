from telegram import ReplyKeyboardMarkup, KeyboardButton
from app.config import ADMIN_IDS

def get_main_keyboard():
    """Основная клавиатура для обычных пользователей"""
    keyboard = [
        [KeyboardButton("👤 Профиль")],
        [KeyboardButton("🎮 Привязать UID"), KeyboardButton("🔓 Отвязать UID")],
        [KeyboardButton("📖 Помощь")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    """Клавиатура для администратора"""
    keyboard = [
        [KeyboardButton("👤 Профиль")],
        [KeyboardButton("🎮 Привязать UID"), KeyboardButton("🔓 Отвязать UID")],
        [KeyboardButton("📖 Помощь")],
        [KeyboardButton("👑 Админ-панель")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_panel_keyboard():
    """Клавиатура админ-панели"""
    keyboard = [
        [KeyboardButton("📊 Статистика"), KeyboardButton("🎡 Призы")],
        [KeyboardButton("📋 Задания"), KeyboardButton("🎫 Выдать билеты")],
        [KeyboardButton("📢 Рассылка")],
        [KeyboardButton("🌙 Выдать луну")],
        [KeyboardButton("➕ Добавить спонсора")],
        [KeyboardButton("🗑 Удалить спонсора")],
        [KeyboardButton("📋 Список спонсоров")],
        [KeyboardButton("🔙 Выйти из админки")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_keyboard_for_user(user_id: int):
    if user_id in ADMIN_IDS:
        return get_admin_keyboard()
    return get_main_keyboard()