from telegram import Update
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.user import User
from app.models.referral import Referral
from app.keyboards import get_keyboard_for_user
from app.handlers.subscription import (
    get_user_subscription_status,
    send_subscription_gate,
    grant_sponsor_reward,
    get_welcome_text,
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
            tickets=0,  # стартовых нет — начислим за подписку
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

        # Проверяем подписку
        status = await get_user_subscription_status(user.id, context.bot)

        if not status["has_access"]:
            # Сбрасываем возможные старые значения
            context.user_data.pop("pending_reward", None)
            await send_subscription_gate(
                update,
                status["missing"],
                context=context,
            )
            return

        # Сразу подписан — награда = total
        reward = status["total"]
        await grant_sponsor_reward(user.id, reward)

        keyboard = get_keyboard_for_user(user.id)
        await update.message.reply_text(
            get_welcome_text(user.first_name, granted=True, reward=reward),
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return

    db.close()

    # ===== СУЩЕСТВУЮЩИЙ ПОЛЬЗОВАТЕЛЬ =====
    status = await get_user_subscription_status(user.id, context.bot)

    if not status["has_access"]:
        # Сбрасываем возможные старые значения — гейт зафиксирует новые при первом показе
        context.user_data.pop("pending_reward", None)
        context.user_data.pop("gate_shown_at", None)
        await send_subscription_gate(
            update,
            status["missing"],
            context=context,
        )
        return

    # Подписан. Награду выдаём только если tickets == 0 (то есть новичок, который сразу подписался)
    # Для старых, кто уже получал раньше — reward будет 0, потому что tickets > 0
    reward_if_new = status["total"]
    granted = await grant_sponsor_reward(user.id, reward_if_new)

    # Считаем reward для отображения: если выдали — total, иначе 0
    display_reward = reward_if_new if granted else 0

    keyboard = get_keyboard_for_user(user.id)
    await update.message.reply_text(
        get_welcome_text(user.first_name, granted=granted, reward=display_reward),
        parse_mode="Markdown",
        reply_markup=keyboard,
    )