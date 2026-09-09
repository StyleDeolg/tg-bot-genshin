from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from app.database import SessionLocal
from app.models.user import User
from app.keyboards import get_keyboard_for_user

# Состояния
WAITING_UID, WAITING_SERVER = range(2)

server_keyboard = ReplyKeyboardMarkup([
    ["🌏 Азия (Asia)", "🌎 США (USA)"],
    ["🌍 Европа (Europe)"]
], resize_keyboard=True)

cancel_keyboard = ReplyKeyboardMarkup([["❌ Отмена"]], resize_keyboard=True)


async def bind_uid_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return ConversationHandler.END

    user = update.effective_user
    db = SessionLocal()
    db_user = db.query(User).filter_by(telegram_id=str(user.id)).first()

    if not db_user:
        await update.message.reply_text("❌ Используйте /start")
        db.close()
        return ConversationHandler.END

    if db_user.genshin_uid:
        keyboard = get_keyboard_for_user(user.id)
        server_map = {"asia": "🌏 Азия", "us": "🌎 США", "eu": "🌍 Европа"}
        server_display = server_map.get(db_user.genshin_server, db_user.genshin_server)
        await update.message.reply_text(
            f"⚠️ У вас уже привязан UID: `{db_user.genshin_uid}` ({server_display})\n"
            f"Используйте `/unbind_uid` чтобы отвязать.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        db.close()
        return ConversationHandler.END

    db.close()
    
    # Устанавливаем флаг, что мы в диалоге привязки
    context.user_data['conversation'] = 'bind_uid'
    
    await update.message.reply_text(
        "🎮 *Привязка Genshin UID*\n\n"
        "Введите ваш UID (9-10 цифр).\n"
        "Для отмены нажмите кнопку ниже.",
        reply_markup=cancel_keyboard,
        parse_mode="Markdown"
    )
    return WAITING_UID


async def bind_uid_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return WAITING_UID

    text = update.message.text.strip()
    
    # Проверяем отмену
    if text == "❌ Отмена":
        context.user_data.pop('conversation', None)
        user_id = update.effective_user.id
        await update.message.reply_text(
            "❌ Привязка отменена.",
            reply_markup=get_keyboard_for_user(user_id)
        )
        return ConversationHandler.END

    # Проверяем, что это UID (9-10 цифр)
    if not text.isdigit() or len(text) not in (9, 10):
        await update.message.reply_text(
            "❌ Неверный формат. Введите 9-10 цифр:",
            reply_markup=cancel_keyboard
        )
        return WAITING_UID

    context.user_data['uid'] = text
    await update.message.reply_text(
        f"✅ Принято: `{text}`\n\n"
        "Теперь выберите регион вашего аккаунта:",
        reply_markup=server_keyboard,
        parse_mode="Markdown"
    )
    return WAITING_SERVER


async def bind_uid_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return WAITING_SERVER

    text = update.message.text.strip()
    
    if text == "❌ Отмена":
        context.user_data.pop('conversation', None)
        user_id = update.effective_user.id
        await update.message.reply_text(
            "❌ Привязка отменена.",
            reply_markup=get_keyboard_for_user(user_id)
        )
        return ConversationHandler.END

    server_map = {
        "🌏 Азия (Asia)": "asia",
        "🌎 США (USA)": "us",
        "🌍 Европа (Europe)": "eu"
    }
    
    server = server_map.get(text)
    if not server:
        await update.message.reply_text(
            "❌ Пожалуйста, выберите регион из кнопок ниже:",
            reply_markup=server_keyboard
        )
        return WAITING_SERVER

    uid = context.user_data.get('uid')
    if not uid:
        await update.message.reply_text("❌ Ошибка. Начните заново с /bind_uid")
        return ConversationHandler.END

    user = update.effective_user
    db = SessionLocal()
    db_user = db.query(User).filter_by(telegram_id=str(user.id)).first()

    if not db_user:
        await update.message.reply_text("❌ Пользователь не найден")
        db.close()
        return ConversationHandler.END

    # Проверяем, не занят ли UID
    existing = db.query(User).filter_by(genshin_uid=uid).first()
    if existing and existing.id != db_user.id:
        await update.message.reply_text(
            f"❌ UID `{uid}` уже привязан к другому пользователю."
        )
        db.close()
        return ConversationHandler.END

    db_user.genshin_uid = uid
    db_user.genshin_server = server
    db.commit()
    db.close()

    # Очищаем состояние
    context.user_data.pop('conversation', None)
    context.user_data.pop('uid', None)
    
    keyboard = get_keyboard_for_user(user.id)

    server_display = {
        "asia": "🌏 Азия",
        "us": "🌎 США",
        "eu": "🌍 Европа"
    }.get(server, server)

    await update.message.reply_text(
        f"✅ *UID успешно привязан!*\n\n"
        f"🎮 UID: `{uid}`\n"
        f"🌍 Регион: {server_display}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    return ConversationHandler.END