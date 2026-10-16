from telegram import Update
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.user import User
from app.models.referral import Referral
from app.keyboards import get_keyboard_for_user
from app.handlers.subscription import (
    get_user_flags,
    get_user_subscription_status,
    send_subscription_gate,
    get_welcome_text_new,
    get_welcome_text_returning,
)
import uuid


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return

    user = update.effective_user
    db = SessionLocal()
    existing = db.query(User).filter_by(telegram_id=str(user.id)).first()

    ref_code = None
    if context.args and len(context.args) > 0:
        arg = context.args[0]
        if arg.startswith("ref_"):
            ref_code = arg.replace("ref_", "")

    # ===== НОВЫЙ ПОЛЬЗОВАТЕЛЬ =====
    if not existing:
        new_user = User(
            telegram_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            public_id=uuid.uuid4(),
            tickets=0,
            sponsor_reward_claimed=False,
            skip_subscription_check=False,
            clicked_sponsors=[],
        )
        db.add(new_user)
        db.flush()

        if ref_code:
            referrer = db.query(User).filter_by(public_id=ref_code).first()
            if referrer and referrer.id != new_user.id:
                existing_ref = db.query(Referral).filter_by(referred_id=new_user.id).first()
                if not existing_ref:
                    referral = Referral(
                        referrer_id=referrer.id,
                        referred_id=new_user.id,
                        reward_claimed=False,
                    )
                    db.add(referral)
                    referrer.tickets += 1
                    db.commit()
                    try:
                        await context.bot.send_message(
                            chat_id=int(referrer.telegram_id),
                            text=(
                                f"🎉 Новый реферал! {new_user.first_name} "
                                f"присоединился по твоей ссылке!\n"
                                f"📊 Ты получил 1 🎟️ билетик!"
                            ),
                        )
                    except Exception as e:
                        print(f"Не удалось отправить уведомление: {e}")

        db.commit()
        db.close()
    else:
        db.close()

    # ===== ФЛАГИ =====
    flags = get_user_flags(user.id)

    if flags["skip_check"]:
        keyboard = get_keyboard_for_user(user.id)
        await update.message.reply_text(
            get_welcome_text_returning(user.first_name),
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return

    # ===== ПРОВЕРКА =====
    is_new = not flags["claimed"]
    status = await get_user_subscription_status(user.id, context.bot)

    # Не всё пройдено — гейт
    if not status["has_access"]:
        context.user_data.pop("gate_shown_at", None)
        await send_subscription_gate(update, context, is_new=is_new)
        return

    # Всё пройдено
    keyboard = get_keyboard_for_user(user.id)

    if is_new:
        # Показываем финальное «✅ Я подписался» (URL-кнопок уже нет)
        context.user_data.pop("gate_shown_at", None)
        await send_subscription_gate(update, context, is_new=True)
        return

    # Уже получал — приветствие
    await update.message.reply_text(
        get_welcome_text_returning(user.first_name),
        parse_mode="Markdown",
        reply_markup=keyboard,
    )