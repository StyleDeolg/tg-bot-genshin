"""
Проверка обязательной подписки на спонсоров.
Работает для публичных и приватных каналов через get_chat_member.

Используется:
- При /start
- При нажатии "✅ Я подписался"
"""
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.sponsor import Sponsor
from app.models.user import User


# Антиспам: не показывать гейт одному пользователю чаще, чем раз в N секунд
GATE_COOLDOWN_SECONDS = 5


async def get_active_sponsors() -> list[dict]:
    """Все активные спонсоры с заполненным channel_id."""
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
        "missing": [ {id, name, link}, ... ],
        "total": int,
        "subscribed_count": int,
        "debug": [ {name, status}, ... ],
    }
    """
    sponsors = await get_active_sponsors()
    if not sponsors:
        return {
            "has_access": True,
            "missing": [],
            "total": 0,
            "subscribed_count": 0,
            "debug": [],
        }

    missing = []
    subscribed_count = 0
    debug = []

    for sp in sponsors:
        try:
            member = await bot.get_chat_member(
                chat_id=int(sp["channel_id"]),
                user_id=int(telegram_id),
            )
            status = member.status
            debug.append({"name": sp["name"], "status": status})

            if status in ("member", "administrator", "creator", "requested"):
                subscribed_count += 1
            else:
                missing.append({
                    "id": sp["id"],
                    "name": sp["name"],
                    "link": sp["link"],
                })
        except Exception as e:
            err = str(e)
            debug.append({"name": sp["name"], "status": f"ERROR: {err[:80]}"})
            print(f"⚠️ [subscription] Ошибка проверки {sp['name']} (id={sp['channel_id']}): {err}")
            # Технические ошибки не блокируют пользователя
            continue

    result = {
        "has_access": len(missing) == 0,
        "missing": missing,
        "total": len(sponsors),
        "subscribed_count": subscribed_count,
        "debug": debug,
    }

    print(f"🔍 [subscription] user={telegram_id} | "
          f"subscribed={subscribed_count}/{len(sponsors)} | "
          f"has_access={result['has_access']}")
    for d in debug:
        print(f"   • {d['name']}: {d['status']}")

    return result


def build_subscription_gate_keyboard(missing: list[dict]) -> InlineKeyboardMarkup:
    """Кнопки на каналы, где пользователь НЕ подписан + '✅ Я подписался'."""
    rows = []
    for sp in missing:
        name = sp.get("name") or "Спонсор"
        link = sp.get("link") or ""
        if link:
            rows.append([InlineKeyboardButton(f"📢 {name}", url=link)])

    rows.append([InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")])
    return InlineKeyboardMarkup(rows)


def get_gate_text(user_name: str, missing: list[dict]) -> str:
    """
    Текст гейта.
    Количество прокрутов = количество каналов, на которые не подписан.
    """
    name = user_name or "пользователь"
    count = len(missing)
    # Склонение: 1 прокрут / 2-4 прокрута / 5+ прокрутов
    if count % 10 == 1 and count % 100 != 11:
        word = "прокрут"
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        word = "прокрута"
    else:
        word = "прокрутов"

    return (
        f"👋 *Привет, {name}!*\n\n"
        f"Добро пожаловать в GenshinPoolBot! 🎡\n\n"
        f"Чтобы получить *{count} бесплатных {word}* и начать выбивать призы, "
        f"выполни простые шаги:\n\n"
        f"📢 *Шаг 1.* Подпишись на наших спонсоров\n"
        f"✅ *Шаг 2.* Нажми «Я подписался»\n"
        f"🎁 *Шаг 3.* Получи доступ + *{count} {word}* в подарок\n\n"
        f"👇 Жми на кнопки ниже:"
    )


def get_welcome_text(user_name: str, granted: bool = True, reward: int = 0) -> str:
    """
    Приветствие для подписанного пользователя — без намёка на спонсоров.
    Если награда выдана — показываем, сколько получил.
    Если уже получал — просто «с возвращением».
    """
    name = user_name or "пользователь"

    if granted:
        # Склонение
        if reward % 10 == 1 and reward % 100 != 11:
            word = "прокрут"
        elif 2 <= reward % 10 <= 4 and (reward % 100 < 10 or reward % 100 >= 20):
            word = "прокрута"
        else:
            word = "прокрутов"

        return (
            f"✦ *Добро пожаловать, {name}!*\n\n"
            f"🎁 Ты получил *{reward} {word}* Колеса Фортуны!\n"
            f"🎡 Крути и выигрывай призы!\n\n"
            f"📖 Используй кнопки внизу для навигации."
        )
    else:
        return (
            f"✦ *С возвращением, {name}!*\n\n"
            f"🎡 Колесо Фортуны ждёт тебя!\n\n"
            f"📖 Используй кнопки внизу для навигации."
        )


async def send_subscription_gate(
    update: Update,
    missing: list[dict],
    context: ContextTypes.DEFAULT_TYPE | None = None,
    is_start: bool = True,
):
    """Отправляет сообщение-гейт с кнопками на каналы, где не подписан."""
    user_id = update.effective_user.id

    # Антиспам
    if context is not None:
        last_shown = context.user_data.get("gate_shown_at", 0)
        now = time.time()
        if now - last_shown < GATE_COOLDOWN_SECONDS:
            print(f"ℹ️ [subscription] Антиспам: пропускаю гейт для {user_id}")
            return
        context.user_data["gate_shown_at"] = now

        # 🔥 Запоминаем размер награды при ПЕРВОМ показе гейта.
        # Если пользователь уже получал когда-то (tickets>0) — ничего не пишем.
        # Иначе фиксируем, сколько он получит, когда подпишется на всех.
        if "pending_reward" not in context.user_data:
            db = SessionLocal()
            try:
                user = db.query(User).filter_by(telegram_id=str(user_id)).first()
                if user and user.tickets == 0:
                    context.user_data["pending_reward"] = len(missing)
                    print(f"📌 [subscription] user={user_id} pending_reward={len(missing)}")
                else:
                    context.user_data["pending_reward"] = 0
            finally:
                db.close()

    keyboard = build_subscription_gate_keyboard(missing)
    user_name = update.effective_user.first_name if update.effective_user else "пользователь"
    text = get_gate_text(user_name, missing)

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


async def grant_sponsor_reward(telegram_id: int, reward: int) -> bool:
    """
    Выдаёт `reward` билетиков.
    Логика: если tickets == 0 → выдаём. Иначе не трогаем (уже получал раньше).
    Возвращает True, если награда была выдана сейчас.
    """
    if reward <= 0:
        return False

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=str(telegram_id)).first()
        if not user:
            print(f"⚠️ [subscription] Пользователь {telegram_id} не найден")
            return False

        if user.tickets == 0:
            user.tickets = reward
            db.commit()
            print(f"✅ [subscription] {telegram_id} получил {reward} билетиков")
            return True

        print(f"ℹ️ [subscription] {telegram_id} уже имеет {user.tickets} билетиков — награду не выдаём")
        return False
    except Exception as e:
        db.rollback()
        print(f"❌ [subscription] Ошибка выдачи {telegram_id}: {e}")
        return False
    finally:
        db.close()


async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатия на '✅ Я подписался'."""
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    user_name = update.effective_user.first_name or "пользователь"

    status = await get_user_subscription_status(telegram_id, context.bot)

    if status["has_access"]:
        # 🔥 Забираем зафиксированную награду (если её ставили в send_subscription_gate).
        # Fallback: если по какой-то причине ничего не зафиксировано, но tickets==0,
        # используем subscribed_count (по факту то же самое — сколько было пропущено).
        reward = context.user_data.pop("pending_reward", 0)
        if reward == 0:
            # Пользователь сразу подписан при первом /start — ему выдаём "total"
            reward = status["total"]

        granted = await grant_sponsor_reward(telegram_id, reward)

        # Убираем гейт
        try:
            await query.message.delete()
        except Exception:
            pass

        from app.keyboards import get_keyboard_for_user

        await context.bot.send_message(
            chat_id=telegram_id,
            text=get_welcome_text(user_name, granted=granted, reward=reward),
            parse_mode="Markdown",
            reply_markup=get_keyboard_for_user(telegram_id),
        )
    else:
        missing = status["missing"]
        keyboard = build_subscription_gate_keyboard(missing)
        text = get_gate_text(user_name, missing)

        try:
            await query.edit_message_text(
                text=text,
                parse_mode="Markdown",
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
        except Exception as e:
            print(f"⚠️ [subscription] Не удалось обновить гейт: {e}")