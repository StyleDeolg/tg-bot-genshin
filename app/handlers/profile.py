from telegram import Update
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.user import User
from app.keyboards import get_keyboard_for_user

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return

    user = update.effective_user
    db = SessionLocal()
    db_user = db.query(User).filter_by(telegram_id=str(user.id)).first()

    if not db_user:
        await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
        db.close()
        return

    db.close()

    keyboard = get_keyboard_for_user(user.id)

    text = (
        f"👤 *Профиль пользователя*\n\n"
        f"🆔 Telegram ID: `{db_user.telegram_id}`\n"
        f"👤 Имя: {db_user.first_name or 'Не указано'}\n"
        f"🔑 Публичный ID: `{db_user.public_id}`\n"
        f"🎟️ Билетики: {db_user.tickets}\n"
        f"💎 Примогемы: {db_user.primogems}\n"
    )

    # Genshin UID теперь хранится прямо в User
    if db_user.genshin_uid:
        server_map = {"asia": "🌏 Азия", "us": "🌎 США", "eu": "🌍 Европа"}
        server = server_map.get(db_user.genshin_server, db_user.genshin_server)
        text += (
            f"\n🎮 *Genshin Impact*\n"
            f"🆔 UID: `{db_user.genshin_uid}`\n"
            f"🌍 Регион: {server}\n"
        )
    else:
        text += f"\n🎮 Genshin UID: *не привязан*\n"
        text += f"Используйте `/bind_uid` для привязки."

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)