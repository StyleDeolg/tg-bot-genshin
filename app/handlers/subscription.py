"""
Проверка обязательной подписки на спонсоров.
Мягкий режим: пользователь жмёт URL-кнопку спонсора + «✅ Отметить»,
и мы считаем спонсора пройденным.
"""
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.sponsor import Sponsor
from app.models.user import User


GATE_COOLDOWN_SECONDS = 5


# =========================================================
# СПОНСОРЫ
# =========================================================

async def get_active_sponsors() -> list[dict]:
    """Все активные спонсоры."""
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
# ФЛАГИ И КЛИКИ
# =========================================================

def get_user_flags(telegram_id: int) -> dict:
    """Один SELECT — флаги + клики."""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=str(telegram_id)).first()
        if not user:
            return {"exists": False, "skip_check": False, "claimed": False, "clicked": []}
        return {
            "exists": True,
            "skip_check": bool(user.skip_subscription_check),
            "claimed": bool(user.sponsor_reward_claimed),
            "clicked": list(user.clicked_sponsors or []),
        }
    finally:
        db.close()


def mark_sponsor_clicked(telegram_id: int, sponsor_id: str) -> None:
    """Записывает ID спонсора в clicked_sponsors, если ещё нет."""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=str(telegram_id)).first()
        if not user:
            return

        clicked = list(user.clicked_sponsors or [])
        if sponsor_id not in clicked:
            clicked.append(sponsor_id)
            user.clicked_sponsors = clicked
            db.commit()
            print(f"👆 [subscription] {telegram_id} отметил {sponsor_id}")
    except Exception as e:
        db.rollback()
        print(f"❌ [subscription] Ошибка записи клика: {e}")
    finally:
        db.close()


# =========================================================
# ПРОВЕРКА ПОДПИСКИ (get_chat_member + клики)
# =========================================================

async def get_user_subscription_status(telegram_id: int, bot) -> dict:
    """
    Возвращает прогресс пользователя:
    - has_access: bool (все спонсоры пройдены)
    - missing: список непройденных
    - passed_ids: список пройденных ID
    - total: всего спонсоров
    """
    flags = get_user_flags(telegram_id)

    if flags["skip_check"]:
        print(f"ℹ️ [subscription] user={telegram_id} — старый, пропускаю")
        return {
            "has_access": True,
            "missing": [],
            "passed_ids": [],
            "total": 0,
            "subscribed_count": 0,
            "is_old": True,
        }

    sponsors = await get_active_sponsors()
    if not sponsors:
        return {
            "has_access": True,
            "missing": [],
            "passed_ids": [],
            "total": 0,
            "subscribed_count": 0,
            "is_old": False,
        }

    clicked = flags["clicked"]

    missing = []
    passed_ids = []
    subscribed_count = 0

    for sp in sponsors:
        # Реальная подписка через Telegram
        is_subscribed = False
        try:
            member = await bot.get_chat_member(
                chat_id=int(sp["channel_id"]),
                user_id=int(telegram_id),
            )
            status = member.status
            if status in ("member", "administrator", "creator", "requested"):
                is_subscribed = True
        except Exception as e:
            print(f"⚠️ [subscription] Ошибка {sp['name']}: {e}")

        # Пройден, если реально подписан ИЛИ кликнул
        is_passed = is_subscribed or (sp["id"] in clicked)

        if is_passed:
            passed_ids.append(sp["id"])
            subscribed_count += 1
        else:
            missing.append({
                "id": sp["id"],
                "name": sp["name"],
                "link": sp["link"],
            })

    result = {
        "has_access": len(missing) == 0,
        "missing": missing,
        "passed_ids": passed_ids,
        "total": len(sponsors),
        "subscribed_count": subscribed_count,
        "is_old": False,
    }

    print(f"🔍 [subscription] user={telegram_id} | "
          f"passed={subscribed_count}/{len(sponsors)} | "
          f"has_access={result['has_access']}")
    return result


# =========================================================
# ВЫДАЧА НАГРАДЫ
# =========================================================

async def grant_sponsor_reward(telegram_id: int, reward: int) -> bool:
    """Выдаёт reward билетиков один раз."""
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


def build_gate_keyboard(sponsors_all: list[dict], passed_ids: list[str]) -> InlineKeyboardMarkup:
    """
    Клавиатура гейта:
    - Для пройденных: «✅ Название» (callback noop)
    - Для непройденных: две кнопки в ряд — «📢 Название» (URL) и «✅ Отметить» (callback)
    - Внизу: «✅ Я подписался»
    """
    passed_set = set(passed_ids)
    rows = []

    for sp in sponsors_all:
        if sp["id"] in passed_set:
            rows.append([InlineKeyboardButton(
                f"✅ {sp['name']}",
                callback_data="noop",
            )])
        else:
            row = []
            if sp.get("link"):
                row.append(InlineKeyboardButton(
                    f"📢 {sp['name']}",
                    url=sp["link"],
                ))
            row.append(InlineKeyboardButton(
                "✅ Отметить",
                callback_data=f"sponsor_clicked_{sp['id']}",
            ))
            rows.append(row)

    rows.append([InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")])
    return InlineKeyboardMarkup(rows)


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
    context: ContextTypes.DEFAULT_TYPE,
    is_new: bool,
):
    """Отправляет гейт с актуальными кнопками."""
    user_id = update.effective_user.id

    # Антиспам
    last_shown = context.user_data.get("gate_shown_at", 0)
    now = time.time()
    if now - last_shown < GATE_COOLDOWN_SECONDS:
        print(f"ℹ️ [subscription] Антиспам: пропускаю гейт для {user_id}")
        return
    context.user_data["gate_shown_at"] = now

    user_name = update.effective_user.first_name or "пользователь"
    sponsors_all = await get_active_sponsors()
    status = await get_user_subscription_status(user_id, context.bot)

    if status["is_old"] or not sponsors_all:
        from app.keyboards import get_keyboard_for_user
        await update.message.reply_text(
            get_welcome_text_returning(user_name),
            parse_mode="Markdown",
            reply_markup=get_keyboard_for_user(user_id),
        )
        return

    keyboard = build_gate_keyboard(sponsors_all, status["passed_ids"])
    text = (
        get_gate_text_new(user_name, status["missing"], status["total"])
        if is_new
        else get_gate_text_returning(user_name, status["missing"])
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


# =========================================================
# ОБРАБОТЧИКИ CALLBACK
# =========================================================

async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатия на '✅ Я подписался'."""
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    user_name = update.effective_user.first_name or "пользователь"

    flags = get_user_flags(telegram_id)

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
        # Обновляем гейт
        sponsors_all = await get_active_sponsors()
        keyboard = build_gate_keyboard(sponsors_all, status["passed_ids"])
        text = (
            get_gate_text_new(user_name, status["missing"], status["total"])
            if is_new
            else get_gate_text_returning(user_name, status["missing"])
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


async def sponsor_clicked_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик клика '✅ Отметить'.
    Записывает ID спонсора в БД и обновляет сообщение.
    """
    query = update.callback_query
    await query.answer("✅ Отмечено!")

    data = query.data  # sponsor_clicked_<uuid>
    sponsor_id = data.replace("sponsor_clicked_", "")
    telegram_id = update.effective_user.id

    mark_sponsor_clicked(telegram_id, sponsor_id)

    # Обновляем сообщение
    user_name = update.effective_user.first_name or "пользователь"
    flags = get_user_flags(telegram_id)
    is_new = not flags["claimed"]

    sponsors_all = await get_active_sponsors()
    status = await get_user_subscription_status(telegram_id, context.bot)

    keyboard = build_gate_keyboard(sponsors_all, status["passed_ids"])
    text = (
        get_gate_text_new(user_name, status["missing"], status["total"])
        if is_new
        else get_gate_text_returning(user_name, status["missing"])
    )

    try:
        await query.edit_message_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"⚠️ [subscription] Ошибка обновления после клика: {e}")


async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Заглушка для ✅ кнопок."""
    await update.callback_query.answer("✅ Уже пройдено")