from telegram import Update
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.user import User


async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик chat_join_request. Ничего не одобряет, ничего не уведомляет.
    Только лог для отладки.
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
            print(f"ℹ️ [join_request] Пользователь {user_id} не найден в БД")
            return
    finally:
        db.close()