from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.user import User
from app.keyboards import get_keyboard_for_user

# Клавиатуры
server_keyboard = ReplyKeyboardMarkup([
    ["🌏 Азия (Asia)", "🌎 США (USA)"],
    ["🌍 Европа (Europe)"]
], resize_keyboard=True)

cancel_keyboard = ReplyKeyboardMarkup([["❌ Отмена"]], resize_keyboard=True)


async def bind_uid_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс привязки UID"""
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id
    db = SessionLocal()
    db_user = db.query(User).filter_by(telegram_id=str(user_id)).first()
    
    if not db_user:
        await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
        db.close()
        return

    if db_user.genshin_uid:
        server_map = {"asia": "🌏 Азия", "us": "🌎 США", "eu": "🌍 Европа"}
        server_display = server_map.get(db_user.genshin_server, db_user.genshin_server)
        await update.message.reply_text(
            f"⚠️ У вас уже привязан UID: `{db_user.genshin_uid}` ({server_display})\n"
            f"Используйте `/unbind_uid` чтобы отвязать.",
            parse_mode="Markdown",
            reply_markup=get_keyboard_for_user(user_id)
        )
        db.close()
        return

    db.close()
    
    # Устанавливаем состояние
    context.user_data['waiting_for_uid'] = True
    context.user_data['uid_step'] = 'waiting_uid'
    
    await update.message.reply_text(
        "🎮 *Привязка Genshin UID*\n\n"
        "Введите ваш UID (9-10 цифр).\n"
        "Для отмены нажмите кнопку ниже.",
        reply_markup=cancel_keyboard,
        parse_mode="Markdown"
    )


async def bind_uid_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод UID"""
    if not update.message:
        return
    
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Если пользователь нажал "Отмена"
    if text == "❌ Отмена":
        context.user_data.clear()
        await update.message.reply_text(
            "❌ Привязка отменена.",
            reply_markup=get_keyboard_for_user(user_id)
        )
        return
    
    step = context.user_data.get('uid_step')
    
    # Шаг 1: Ожидание UID
    if step == 'waiting_uid':
        if not text.isdigit() or len(text) not in (9, 10):
            await update.message.reply_text(
                "❌ Неверный формат. Введите 9-10 цифр:",
                reply_markup=cancel_keyboard
            )
            return
        
        # Сохраняем UID и переходим к выбору региона
        context.user_data['uid'] = text
        context.user_data['uid_step'] = 'waiting_server'
        
        await update.message.reply_text(
            f"✅ Принято: `{text}`\n\n"
            "Теперь выберите регион вашего аккаунта:",
            reply_markup=server_keyboard,
            parse_mode="Markdown"
        )
    
    # Шаг 2: Ожидание региона
    elif step == 'waiting_server':
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
            return
        
        uid = context.user_data.get('uid')
        if not uid:
            await update.message.reply_text("❌ Ошибка. Начните заново с /bind_uid")
            context.user_data.clear()
            return
        
        # Сохраняем в БД
        db = SessionLocal()
        db_user = db.query(User).filter_by(telegram_id=str(user_id)).first()
        
        if not db_user:
            await update.message.reply_text("❌ Пользователь не найден")
            db.close()
            context.user_data.clear()
            return
        
        # Проверяем, не занят ли UID
        existing = db.query(User).filter_by(genshin_uid=uid).first()
        if existing and existing.id != db_user.id:
            await update.message.reply_text(
                f"❌ UID `{uid}` уже привязан к другому пользователю."
            )
            db.close()
            context.user_data.clear()
            return
        
        db_user.genshin_uid = uid
        db_user.genshin_server = server
        db.commit()
        db.close()
        
        # Очищаем состояние
        context.user_data.clear()
        
        server_display = {
            "asia": "🌏 Азия",
            "us": "🌎 США",
            "eu": "🌍 Европа"
        }.get(server, server)
        
        await update.message.reply_text(
            f"✅ *UID успешно привязан!*\n\n"
            f"🎮 UID: `{uid}`\n"
            f"🌍 Регион: {server_display}",
            reply_markup=get_keyboard_for_user(user_id),
            parse_mode="Markdown"
        )