from telegram import Update
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.user import User
from app.keyboards import get_keyboard_for_user

async def unbind_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отвязывает Genshin UID"""
    if not update.effective_user or not update.message:
        return

    user = update.effective_user
    db = SessionLocal()
    db_user = db.query(User).filter_by(telegram_id=str(user.id)).first()

    if not db_user:
        await update.message.reply_text("❌ Используйте /start")
        db.close()
        return

    if not db_user.genshin_uid:
        keyboard = get_keyboard_for_user(user.id)
        await update.message.reply_text(
            "❌ У вас нет привязанного UID.\n"
            "Используйте `/bind_uid` для привязки.",
            reply_markup=keyboard
        )
        db.close()
        return

    uid = db_user.genshin_uid
    server = db_user.genshin_server
    db_user.genshin_uid = None
    db_user.genshin_server = None
    db.commit()
    db.close()

    keyboard = get_keyboard_for_user(user.id)
    await update.message.reply_text(
        f"✅ UID `{uid}` ({server}) успешно отвязан.\n"
        f"Чтобы привязать новый, используйте `/bind_uid`.",
        reply_markup=keyboard
    )