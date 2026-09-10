from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from app.database import SessionLocal
from app.models.user import User
from app.models.sponsor import Sponsor
from app.models.task import Task, UserTask


async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает событие chat_join_request.
    Срабатывает, когда пользователь подаёт заявку на вступление в канал,
    где бот является администратором с правом 'Приглашать пользователей'.
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
        # 1. Ищем спонсора по channel_id
        sponsor = db.query(Sponsor).filter_by(
            channel_id=chat_id,
            is_active=True
        ).first()

        if not sponsor:
            print(f"⚠️ [join_request] Спонсор для канала {chat_id} не найден")
            return

        # 2. Ищем пользователя в БД
        user = db.query(User).filter_by(telegram_id=str(user_id)).first()
        if not user:
            print(f"⚠️ [join_request] Пользователь {user_id} не найден в БД")
            # Всё равно пробуем уведомить, но награду не даём
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"📥 Твоя заявка в *{chat_title}* подана!\n"
                        f"ℹ️ Но ты ещё не зарегистрирован в боте. Нажми /start."
                    ),
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            return

        # 3. Ищем задание спонсора
        task = db.query(Task).filter_by(
            sponsor_id=sponsor.id,
            is_active=True,
            task_type="sponsor"
        ).first()

        if not task:
            print(f"⚠️ [join_request] Задание для спонсора {sponsor.name} не найдено")
            return

        # 4. Проверяем, не выполнено ли уже
        user_task = db.query(UserTask).filter_by(
            user_id=user.id,
            task_id=task.id
        ).first()

        if user_task and user_task.completed_at:
            print(f"ℹ️ [join_request] Пользователь {user_id} уже получил награду")
            return

        # 5. Выдаём награду
        reward = task.reward or 1
        user.tickets += reward

        if not user_task:
            user_task = UserTask(
                user_id=user.id,
                task_id=task.id,
                progress=1,
                completed_at=datetime.now()
            )
            db.add(user_task)
        else:
            user_task.completed_at = datetime.now()
            user_task.progress = 1

        db.commit()

        print(f"✅ [join_request] Награда ({reward}) выдана пользователю {user_id} за заявку в {chat_title}")

        # 6. Уведомляем пользователя в ЛС
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"✅ Заявка на вступление в *{chat_title}* подана!\n"
                    f"🎁 Ты получил {reward} билетик(ов)!\n"
                    f"ℹ️ Как только админ одобрит заявку, ты станешь участником канала."
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"⚠️ [join_request] Не удалось отправить ЛС {user_id}: {e}")

        # 7. (Опционально) Автоматически одобрить заявку.
        # Раскомментируй, если хочешь, чтобы бот сразу впускал пользователя:
        # try:
        #     await context.bot.approve_chat_join_request(
        #         chat_id=chat_id,
        #         user_id=user_id
        #     )
        #     print(f"✅ [join_request] Заявка {user_id} автоматически одобрена")
        # except Exception as e:
        #     print(f"⚠️ [join_request] Не удалось одобрить заявку: {e}")

    except Exception as e:
        db.rollback()
        print(f"❌ [join_request] Ошибка обработки заявки: {e}")
    finally:
        db.close()