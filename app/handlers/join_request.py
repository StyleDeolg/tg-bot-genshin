from telegram import Update
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.user import User


async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик события chat_join_request.
    Наград не выдаёт — они выдаются через /start.
    """
    request = update.chat_join_request
    if not request:
        return

    user_id = request.from_user.id
    chat_id = request.chat.id
    chat_title = request.chat.title or "канал"

    print(f"📥 [join_request] Заявка от {user_id} в канал {chat_id} ({chat_title})")

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=str(user_id)).first()
        if not user:
            print(f"⚠️ [join_request] Пользователь {user_id} не найден в БД")
            return

        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"📥 Твоя заявка в *{chat_title}* подана!\n\n"
                    f"✅ Доступ к боту открыт.\n"
                    f"ℹ️ Как только админ одобрит заявку — станешь участником канала."
                ),
                parse_mode="Markdown",
            )
        except Exception as e:
            print(f"⚠️ [join_request] Не удалось отправить ЛС {user_id}: {e}")

    finally:
        db.close()