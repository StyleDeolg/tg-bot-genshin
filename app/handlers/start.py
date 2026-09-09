from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.user import User
from app.models.referral import Referral
from app.keyboards import get_keyboard_for_user
from app.config import config  # 👈 ИМПОРТИРУЕМ config
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

    if not existing:
        new_user = User(
            telegram_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            public_id=uuid.uuid4(),
            tickets=4,
            primogems=0,
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
                        reward_claimed=False
                    )
                    db.add(referral)
                    referrer.tickets += 3
                    new_user.tickets += 1
                    db.commit()
                    try:
                        await context.bot.send_message(
                            chat_id=int(referrer.telegram_id),
                            text=f"🎉 Новый реферал! {new_user.first_name} присоединился по твоей ссылке!\n📊 Ты получил 3 🎟️ билетика!"
                        )
                    except Exception as e:
                        print(f"Не удалось отправить уведомление: {e}")
        
        db.commit()
        
        keyboard = get_keyboard_for_user(user.id)
        
        await update.message.reply_text(
            f"👋 Привет, {user.first_name or 'пользователь'}!\n\n"
            f"Добро пожаловать в Genshin Impact Community Bot!\n"
            f"🎁 Ты получил 2 бонусных билетика за регистрацию!\n"
            f"🎡 Крути колесо, получай примогемы и выполняй задания!\n\n"
            f"📖 Используй кнопки внизу для навигации.",
            reply_markup=keyboard
        )
    else:
        keyboard = get_keyboard_for_user(user.id)
        await update.message.reply_text(
            f"👋 С возвращением, {user.first_name or 'пользователь'}!\n\n"
            f"📖 Используй кнопки внизу для навигации.",
            reply_markup=keyboard
        )
    db.close()