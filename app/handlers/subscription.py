"""
Проверка обязательной подписки на спонсоров.
Работает для публичных и приватных каналов через get_chat_member.
"""
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.sponsor import Sponsor
from app.models.user import User


GATE_COOLDOWN_SECONDS = 5


# =========================================================
# ПОЛУЧЕНИЕ СПОНСОРОВ И СТАТУСОВ
# =========================================================

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
        "has_access": bool,               # подписан на всех
        "missing": [ {name, link}, ... ], # на кого не подписан
        "total": int,
        "subscribed_count": int,
    }
    """
    sponsors = await get_active_sponsors()
    if not sponsors:
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
            status = member.status
            # 🔥 'requested' — заявка тоже считается подпиской
            if status in ("member", "administrator", "creator", "requested"):
                subscribed_count += 1
                print(f"   • {sp['name']}: {status} ✅")
            else:
                missing.append({
                    "name": sp["name"],
                    "link": sp["link"],
                })
                print(f"   • {sp['name']}: {status} ❌")
        except Exception as e:
            print(f"⚠️ [subscription] Ошибка проверки {sp['name']}: {e}")
            # Технические ошибки пропускаем — не блокируем
            continue

    result = {
        "has_access": len(missing) == 0,
        "missing": missing,
        "total": len(sponsors),
        "subscribed_count": subscribed_count,
    }

    print(f"🔍 [subscription] user={telegram_id} | "
          f"subscribed={subscribed_count}/{len(sponsors)} | "
          f"has_access={result['has_access']}")
    return result


# =========================================================
# РАБОТА С НАГРАДОЙ
# =========================================================

def has_claimed_reward(telegram_id: int) -> bool:
    """Получал ли пользователь награду за подписку."""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=str(telegram_id)).first()
        if not user:
            return False
        return bool(user.sponsor_reward_claimed)
    finally:
        db.close()


async def grant_sponsor_reward(telegram_id: int, reward: int) -> bool:
    """
    Выдаёт reward билетиков и ставит флаг sponsor_reward_claimed=True.
    Возвращает True, если награда выдана (или уже была).
    """
    if reward <= 0:
        return False

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=str(telegram_id)).first()
        if not user:
            print(f"⚠️ [subscription] Пользователь {telegram_id} не найден")
            return False

        if user.sponsor_reward_claimed:
            print(f"ℹ️ [subscription] {telegram_id} уже получал награду")
            return False

        user.tickets += reward
        user.sponsor_reward_claimed = True
        db.commit()
        print(f"✅ [subscription] {telegram_id} получил {reward} билетиков")
        return True

    except Exception as e:
        db.rollback()
        print(f"❌ [subscription] Ошибка выдачи {telegram_id}: {e}")
        return False
    finally:
        db.close()


# =========================================================
# ТЕКСТЫ И КЛАВИАТУРА ГЕЙТА
# =========================================================

def _pluralize(count: int, one: str, few: str, many: str) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return one
    if 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return few
    return many


def build_subscription_gate_keyboard(missing: list[dict]) -> InlineKeyboardMarkup:
    """Кнопки на каналы, где не подписан + '✅ Я подписался'."""
    rows = []
    for sp in missing:
        name = sp.get("name") or "Спонсор"
        link = sp.get("link") or ""
        if link:
            rows.append([InlineKeyboardButton(f"📢 {name}", url=link)])

    rows.append([InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")])
    return InlineKeyboardMarkup(rows)


def get_gate_text_new(user_name: str, missing: list[dict]) -> str:
    """
    Текст гейта для НОВОГО пользователя (ещё не получал награду).
    Обещаем N прокрутов.
    """
    name = user_name or "пользователь"
    count = len(missing)
    word = _pluralize(count, "прокрут", "прокрута", "прокрутов")

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


def get_gate_text_returning(user_name: str, missing: list[dict]) -> str:
    """
    Текст гейта для СТАРОГО пользователя (уже получал награду).
    Без обещания награды.
    """
    name = user_name or "пользователь"
    count = len(missing)

    return (
        f"👋 *Привет, {name}!*\n\n"
        f"Чтобы бот снова заработал, подпишись на наших спонсоров:\n\n"
        f"📢 Подпишись на каналы ниже\n"
        f"✅ И нажми «Я подписался»\n\n"
        f"👇 Осталось подписаться: *{count}*"
    )


def get_welcome_text_new(user_name: str, reward: int) -> str:
    """Приветствие для НОВОГО — с наградой."""
    name = user_name or "пользователь"
    word = _pluralize(reward, "прокрут", "прокрута", "прокрутов")

    return (
        f"✦ *Добро пожаловать, {name}!*\n\n"
        f"🎁 Ты получил *{reward} {word}* Колеса Фортуны!\n"
        f"🎡 Крути и выигрывай призы!\n\n"
        f"📖 Используй кнопки внизу для навигации."
    )


def get_welcome_text_returning(user_name: str) -> str:
    """Приветствие для СТАРОГО — без награды."""
    name = user_name or "пользователь"

    return (
        f"✦ *С возвращением, {name}!*\n\n"
        f"🎡 Колесо Фортуны ждёт тебя!\n\n"
        f"📖 Используй кнопки внизу для навигации."
    )


async def send_subscription_gate(
    update: Update,
    missing: list[dict],
    is_new: bool,
    context: ContextTypes.DEFAULT_TYPE | None = None,
):
    """
    Отправляет гейт.
    is_new=True  → текст с наградой
    is_new=False → текст без награды
    """
    user_id = update.effective_user.id

    # Антиспам
    if context is not None:
        last_shown = context.user_data.get("gate_shown_at", 0)
        now = time.time()
        if now - last_shown < GATE_COOLDOWN_SECONDS:
            print(f"ℹ️ [subscription] Антиспам: пропускаю гейт для {user_id}")
            return
        context.user_data["gate_shown_at"] = now

    keyboard = build_subscription_gate_keyboard(missing)
    user_name = update.effective_user.first_name if update.effective_user else "пользователь"

    text = (
        get_gate_text_new(user_name, missing)
        if is_new
        else get_gate_text_returning(user_name, missing)
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


# =========================================================
# ОБРАБОТЧИК КНОПКИ "✅ Я ПОДПИСАЛСЯ"
# =========================================================

async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатия на '✅ Я подписался'."""
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    user_name = update.effective_user.first_name or "пользователь"

    is_new = not has_claimed_reward(telegram_id)

    status = await get_user_subscription_status(telegram_id, context.bot)

    if status["has_access"]:
        # 🔥 Выдаём награду только здесь (если ещё не получал)
        if is_new:
            reward = len(status["missing"]) + len(status.get("rewardable", []))
            # rewardable у нас больше нет — считаем по подпискам:
            # сколько всего спонсоров, столько и награда
            reward = status["total"]
            granted = await grant_sponsor_reward(telegram_id, reward)
            reward_text = reward if granted else 0
        else:
            reward_text = 0

        # Убираем гейт
        try:
            await query.message.delete()
        except Exception:
            pass

        from app.keyboards import get_keyboard_for_user

        if is_new:
            await context.bot.send_message(
                chat_id=telegram_id,
                text=get_welcome_text_new(user_name, reward_text),
                parse_mode="Markdown",
                reply_markup=get_keyboard_for_user(telegram_id),
            )
        else:
            await context.bot.send_message(
                chat_id=telegram_id,
                text=get_welcome_text_returning(user_name),
                parse_mode="Markdown",
                reply_markup=get_keyboard_for_user(telegram_id),
            )
    else:
        # Обновляем гейт — только оставшиеся каналы
        missing = status["missing"]
        keyboard = build_subscription_gate_keyboard(missing)
        text = (
            get_gate_text_new(user_name, missing)
            if is_new
            else get_gate_text_returning(user_name, missing)
        )

        try:
            await query.edit_message_text(
                text=text,
                parse_mode="Markdown",
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
        except Exception as e:
            print(f"⚠️ [subscription] Не удалось обновить гейт: {e}")