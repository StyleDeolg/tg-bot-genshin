from telegram import ReplyKeyboardMarkup, KeyboardButton
from app.config import ADMIN_IDS

def get_main_keyboard():
    """Основная клавиатура для обычных пользователей"""
    keyboard = [
        [KeyboardButton("👤 Профиль"), KeyboardButton("💎 Донаты")],
        [KeyboardButton("🎮 Привязать UID"), KeyboardButton("🔓 Отвязать UID")],
        [KeyboardButton("📖 Помощь")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    """Клавиатура для администратора (с доп. кнопкой)"""
    keyboard = [
        [KeyboardButton("👤 Профиль"), KeyboardButton("💎 Донаты")],
        [KeyboardButton("🎮 Привязать UID"), KeyboardButton("🔓 Отвязать UID")],
        [KeyboardButton("📖 Помощь")],
        [KeyboardButton("👑 Админ-панель")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_keyboard_for_user(user_id: int):
    """Возвращает правильную клавиатуру в зависимости от прав пользователя"""
    if user_id in ADMIN_IDS:
        return get_admin_keyboard()
    return get_main_keyboard()