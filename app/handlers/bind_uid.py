from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from app.database import SessionLocal
from app.models.user import User
from app.keyboards import get_keyboard_for_user

# Состояния
WAITING_UID, WAITING_CONFIRM, WAITING_SERVER = range(3)

server_keyboard = ReplyKeyboardMarkup([
    ["🌏 Азия", "🌎 США"],
    ["🌍 Европа"]
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
        await update.message.reply_text(
            f"⚠️ У вас уже привязан UID: `{db_user.genshin_uid}` ({db_user.genshin_server})\n"
            f"Используйте `/unbind_uid` чтобы отвязать.",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        db.close()
        return ConversationHandler.END

    db.close()
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

    if update.message.text == "❌ Отмена":
        await update.message.reply_text("❌ Привязка отменена.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    uid = update.message.text.strip() if update.message.text else ""
    if not uid.isdigit() or len(uid) not in (9, 10):
        await update.message.reply_text(
            "❌ Неверный формат. Введите 9-10 цифр:",
            reply_markup=cancel_keyboard
        )
        return WAITING_UID

    context.user_data['uid'] = uid
    await update.message.reply_text(
        f"✅ Принято: `{uid}`\n\n"
        "Теперь выберите регион вашего аккаунта:",
        reply_markup=server_keyboard,
        parse_mode="Markdown"
    )
    return WAITING_SERVER

async def bind_uid_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return WAITING_SERVER

    if update.message.text == "❌ Отмена":
        await update.message.reply_text("❌ Привязка отменена.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    server_map = {
        "🌏 Азия": "asia",
        "🌎 США": "us",
        "🌍 Европа": "eu"
    }
    
    server = server_map.get(update.message.text)
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
    if existing:
        await update.message.reply_text(
            f"❌ UID `{uid}` уже привязан к другому пользователю."
        )
        db.close()
        return ConversationHandler.END

    db_user.genshin_uid = uid
    db_user.genshin_server = server
    db.commit()
    db.close()

    context.user_data.clear()
    keyboard = get_keyboard_for_user(user.id)

    await update.message.reply_text(
        f"✅ *UID успешно привязан!*\n\n"
        f"🎮 UID: `{uid}`\n"
        f"🌍 Регион: {update.message.text}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    return ConversationHandler.END