"""
Проверка обязательной подписки на спонсоров.
Используется в боте и в API.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.sponsor import Sponsor
from app.models.task import Task
from app.models.user import User

# ===== КЭШ СОСТОЯНИЯ ГЕЙТА =====
# Чтобы не спамить пользователя гейтом на каждое сообщение
# храним в context.user_data['gate_shown_at'] timestamp


async def get_active_sponsors() -> list[dict]:
    """Возвращает список активных спонсоров (только те, у кого есть канал)"""
    db = SessionLocal()
    try:
        sponsors = db.query(Sponsor).filter(
            Sponsor.is_active == True,
            Sponsor.channel_id.isnot(None),
        ).all()
        return [
            {
                "id": str(s.id),
                "name": s.name or "Спонсор",
                "link": s.link,
                "channel_id": s.channel_id,
                "channel": s.channel,
            }
            for s in sponsors
        ]
    finally:
        db.close()


async def get_user_subscription_status(telegram_id: int, bot) -> dict:
    """
    Проверяет подписку пользователя на всех активных спонсоров.
    Возвращает:
    {
        "has_access": bool,
        "missing": [ {id, name, link}, ... ],   # на кого не подписан
        "total": int,
        "subscribed_count": int,
    }
    """
    sponsors = await get_active_sponsors()
    if not sponsors:
        # Нет спонсоров — доступ у всех
        return {
            "has_access": True,
            "missing": [],
            "total": 0,
            "subscribed_count": 0,
        }

    missing = []
    subscribed_count = 0

    for sp in sponsors:
        try:
            member = await bot.get_chat_member(
                chat_id=int(sp["channel_id"]),
                user_id=int(telegram_id),
            )
            # 🔥 ВАЖНО: разрешаем 'requested' — заявка уже считается доступом
            if member.status in ("member", "administrator", "creator", "requested"):
                subscribed_count += 1
            else:
                missing.append({
                    "id": sp["id"],
                    "name": sp["name"],
                    "link": sp["link"],
                })
        except Exception as e:
            # Если бот не админ в канале — считаем, что пользователь не подписан
            print(f"⚠️ [subscription] Ошибка проверки {sp['name']}: {e}")
            missing.append({
                "id": sp["id"],
                "name": sp["name"],
                "link": sp["link"],
            })

    return {
        "has_access": len(missing) == 0,
        "missing": missing,
        "total": len(sponsors),
        "subscribed_count": subscribed_count,
    }


def build_subscription_gate_keyboard(missing: list[dict]) -> InlineKeyboardMarkup:
    """
    Строит inline-клавиатуру с кнопками-ссылками на каналы.
    Каждая кнопка открывает канал (или подаёт заявку, если приватный).
    Плюс кнопка "✅ Я подписался" с callback_data="check_subscription".
    """
    rows = []
    for sp in missing:
        name = sp.get("name") or "Спонсор"
        link = sp.get("link") or ""
        if link:
            rows.append([InlineKeyboardButton(f"📢 {name}", url=link)])

    rows.append([InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")])
    return InlineKeyboardMarkup(rows)


async def send_subscription_gate(update: Update, missing: list[dict], is_start: bool = False):
    """Отправляет сообщение-гейт с кнопками спонсоров"""
    keyboard = build_subscription_gate_keyboard(missing)

    if is_start:
        text = (
            "👋 *Привет!*\n\n"
            "Чтобы пользоваться ботом, подпишись на наших спонсоров:\n\n"
            f"Осталось подписаться: *{len(missing)}*"
        )
    else:
        text = (
            "🔒 *Доступ к боту закрыт*\n\n"
            "Чтобы пользоваться ботом, подпишись на всех спонсоров:\n\n"
            f"Осталось подписаться: *{len(missing)}*"
        )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатия на '✅ Я подписался'"""
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    status = await get_user_subscription_status(telegram_id, context.bot)

    if status["has_access"]:
        # Убираем гейт
        try:
            await query.message.delete()
        except Exception:
            pass

        # Приветствие + меню
        from app.keyboards import get_keyboard_for_user
        await context.bot.send_message(
            chat_id=telegram_id,
            text="✅ *Подписка подтверждена!*\n\nДобро пожаловать в бота!",
            parse_mode="Markdown",
            reply_markup=get_keyboard_for_user(telegram_id),
        )
    else:
        # Обновляем гейт
        missing = status["missing"]
        keyboard = build_subscription_gate_keyboard(missing)
        try:
            await query.edit_message_text(
                text=(
                    "🔒 *Доступ к боту закрыт*\n\n"
                    "Чтобы пользоваться ботом, подпишись на всех спонсоров:\n\n"
                    f"Осталось подписаться: *{len(missing)}*"
                ),
                parse_mode="Markdown",
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
        except Exception as e:
            print(f"⚠️ [subscription] Не удалось обновить гейт: {e}")