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
# ПОЛУЧЕНИЕ СПОНСОРОВ
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


# =========================================================
# ФЛАГИ ПОЛЬЗОВАТЕЛЯ (один SELECT — все флаги)
# =========================================================

def get_user_flags(telegram_id: int) -> dict:
    """
    Возвращает флаги пользователя одним запросом:
    - exists: есть ли в БД
    - skip_check: пропускать ли проверку подписки (старый юзер)
    - claimed: получал ли награду
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=str(telegram_id)).first()
        if not user:
            return {"exists": False, "skip_check": False, "claimed": False}
        return {
            "exists": True,
            "skip_check": bool(user.skip_subscription_check),
            "claimed": bool(user.sponsor_reward_claimed),
        }
    finally:
        db.close()


# =========================================================
# ПРОВЕРКА ПОДПИСКИ
# =========================================================

async def get_user_subscription_status(telegram_id: int, bot) -> dict:
    """
    Проверяет подписку на всех спонсоров.
    Если пользователь «старый» (skip_subscription_check=True) — пропускает.
    """
    # 🔥 Старый пользователь — пропуск без проверки
    flags = get_user_flags(telegram_id)
    if flags["skip_check"]:
        print(f"ℹ️ [subscription] user={telegram_id} — старый, пропускаю проверку")
        return {
            "has_access": True,
            "missing": [],
            "total": 0,
            "subscribed_count": 0,
            "is_old": True,
        }

    sponsors = await get_active_sponsors()
    if not sponsors:
        return {
            "has_access": True,
            "missing": [],
            "total": 0,
            "subscribed_count": 0,
            "is_old": False,
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
            if status in ("member", "administrator", "creator", "requested"):
                subscribed_count += 1
                print(f"   • {sp['name']}: {status} ✅")
            else:
                missing.append({"name": sp["name"], "link": sp["link"]})
                print(f"   • {sp['name']}: {status} ❌")
        except Exception as e:
            print(f"⚠️ [subscription] Ошибка проверки {sp['name']}: {e}")
            continue

    result = {
        "has_access": len(missing) == 0,
        "missing": missing,
        "total": len(sponsors),
        "subscribed_count": subscribed_count,
        "is_old": False,
    }

    print(f"🔍 [subscription] user={telegram_id} | "
          f"subscribed={subscribed_count}/{len(sponsors)} | "
          f"has_access={result['has_access']}")
    return result


# =========================================================
# ВЫДАЧА НАГРАДЫ
# =========================================================

async def grant_sponsor_reward(telegram_id: int, reward: int) -> bool:
    """Выдаёт reward билетиков один раз (флаг sponsor_reward_claimed)."""
    if reward <= 0:
        return False

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=str(telegram_id)).first()
        if not user:
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
# ТЕКСТЫ И КЛАВИАТУРА
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


def build_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура только с '✅ Я подписался' — когда URL-кнопок нет."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")]
    ])


def get_gate_text_new(user_name: str, missing: list[dict], total: int) -> str:
    """Гейт для НОВОГО — с обещанием награды."""
    name = user_name or "пользователь"
    word = _pluralize(total, "прокрут", "прокрута", "прокрутов")

    return (
        f"👋 *Привет, {name}!*\n\n"
        f"Добро пожаловать в GenshinPoolBot! 🎡\n\n"
        f"Чтобы получить *{total} бесплатных {word}* и начать выбивать призы, "
        f"выполни простые шаги:\n\n"
        f"📢 *Шаг 1.* Подпишись на наших спонсоров\n"
        f"✅ *Шаг 2.* Нажми «Я подписался»\n"
        f"🎁 *Шаг 3.* Получи доступ + *{total} {word}* в подарок\n\n"
        f"👇 Жми на кнопки ниже:"
    )


def get_gate_text_returning(user_name: str, missing: list[dict]) -> str:
    """Гейт для СТАРОГО — без обещания награды."""
    name = user_name or "пользователь"

    return (
        f"👋 *Привет, {name}!*\n\n"
        f"Чтобы бот снова заработал, подпишись на наших спонсоров:\n\n"
        f"📢 Подпишись на каналы ниже\n"
        f"✅ И нажми «Я подписался»\n\n"
        f"👇 Осталось подписаться: *{len(missing)}*"
    )


def get_welcome_text_new(user_name: str, reward: int) -> str:
    """Приветствие для НОВОГО после награды."""
    name = user_name or "пользователь"
    word = _pluralize(reward, "прокрут", "прокрута", "прокрутов")

    return (
        f"✦ *Добро пожаловать, {name}!*\n\n"
        f"🎁 Ты получил *{reward} {word}* Колеса Фортуны!\n"
        f"🎡 Крути и выигрывай призы!\n\n"
        f"📖 Используй кнопки внизу для навигации."
    )


def get_welcome_text_returning(user_name: str) -> str:
    """Приветствие для СТАРОГО."""
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
    total_sponsors: int,
    context: ContextTypes.DEFAULT_TYPE | None = None,
    hide_urls: bool = False,
):
    """Отправляет гейт с антиспамом."""
    user_id = update.effective_user.id

    if context is not None:
        last_shown = context.user_data.get("gate_shown_at", 0)
        now = time.time()
        if now - last_shown < GATE_COOLDOWN_SECONDS:
            print(f"ℹ️ [subscription] Антиспам: пропускаю гейт для {user_id}")
            return
        context.user_data["gate_shown_at"] = now

    keyboard = build_confirm_keyboard() if hide_urls else build_subscription_gate_keyboard(missing)
    user_name = update.effective_user.first_name if update.effective_user else "пользователь"

    text = (
        get_gate_text_new(user_name, missing, total_sponsors)
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

    flags = get_user_flags(telegram_id)

    # 🔥 Старый пользователь — просто приветствие
    if flags["skip_check"]:
        try:
            await query.message.delete()
        except Exception:
            pass

        from app.keyboards import get_keyboard_for_user
        await context.bot.send_message(
            chat_id=telegram_id,
            text=get_welcome_text_returning(user_name),
            parse_mode="Markdown",
            reply_markup=get_keyboard_for_user(telegram_id),
        )
        return

    is_new = not flags["claimed"]

    status = await get_user_subscription_status(telegram_id, context.bot)

    if status["has_access"]:
        # Выдаём награду, если ещё не получал
        if is_new:
            reward = status["total"]
            granted = await grant_sponsor_reward(telegram_id, reward)
            reward_text = reward if granted else 0
        else:
            reward_text = 0

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
        # Обновляем гейт — показываем только оставшиеся каналы
        missing = status["missing"]
        keyboard = build_subscription_gate_keyboard(missing)
        text = (
            get_gate_text_new(user_name, missing, status["total"])
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