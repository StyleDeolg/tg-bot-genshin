from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from app.config import config  # 👈 ИМПОРТИРУЕМ config


def get_main_keyboard():
    """Основная клавиатура для пользователя"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("👤 Профиль"), KeyboardButton("🎡 Крутить колесо")],
        [KeyboardButton("📋 Задания"), KeyboardButton("👥 Рефералы")],
        [KeyboardButton("💎 Донаты"), KeyboardButton("📖 Помощь")]
    ], resize_keyboard=True)


def get_keyboard_for_user(user_id: int):
    """Клавиатура для пользователя с админ-кнопкой"""
    keyboard = [
        [KeyboardButton("👤 Профиль"), KeyboardButton("🎡 Крутить колесо")],
        [KeyboardButton("📋 Задания"), KeyboardButton("👥 Рефералы")],
        [KeyboardButton("💎 Донаты"), KeyboardButton("📖 Помощь")]
    ]
    
    # 👇 ИСПОЛЬЗУЕМ config.ADMIN_IDS (свойство)
    if user_id in config.ADMIN_IDS:
        keyboard.append([KeyboardButton("👑 Админ-панель")])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_admin_keyboard():
    """Клавиатура для админа"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("👤 Профиль"), KeyboardButton("🎡 Крутить колесо")],
        [KeyboardButton("📋 Задания"), KeyboardButton("👥 Рефералы")],
        [KeyboardButton("💎 Донаты"), KeyboardButton("📖 Помощь")],
        [KeyboardButton("👑 Админ-панель")]
    ], resize_keyboard=True)


def get_admin_panel_keyboard():
    """Клавиатура админ-панели"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("📊 Статистика"), KeyboardButton("🎡 Призы")],
        [KeyboardButton("📋 Задания"), KeyboardButton("🎫 Выдать билеты")],
        [KeyboardButton("📢 Рассылка"), KeyboardButton("🌙 Выдать луну")],
        [KeyboardButton("➕ Добавить спонсора"), KeyboardButton("🗑 Удалить спонсора")],
        [KeyboardButton("📋 Список спонсоров")],
        [KeyboardButton("🔙 Выйти из админки")]
    ], resize_keyboard=True)


def get_cancel_keyboard():
    """Клавиатура с кнопкой отмены"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("❌ Отмена")]
    ], resize_keyboard=True)