"""
Проверка обязательной подписки на спонсоров.
Один источник правды — user_tasks (completed_at).

Используется:
- При /start
- При нажатии "✅ Я подписался"
"""
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.sponsor import Sponsor
from app.models.task import Task, UserTask
from app.models.user import User


GATE_COOLDOWN_SECONDS = 5


# =========================================================
# 1. ПОЛУЧЕНИЕ СПОНСОРОВ И СТАТУСОВ
# =========================================================

async def get_active_sponsors_with_tasks() -> list[dict]:
    """
    Возвращает активных спонсоров с их task_id.
    Задание спонсора нужно для отслеживания user_task.completed_at.
    """
    db = SessionLocal()
    try:
        sponsors = db.query(Sponsor).filter(
            Sponsor.is_active == True,
            Sponsor.channel_id.isnot(None),
        ).all()

        result = []
        for sp in sponsors:
            task = db.query(Task).filter_by(
                sponsor_id=sp.id,
                task_type="sponsor",
                is_active=True,
            ).first()

            result.append({
                "sponsor_id": str(sp.id),
                "task_id": str(task.id) if task else None,
                "name": sp.name or "Спонсор",
                "link": sp.link,
                "channel_id": sp.channel_id,
            })
        return result
    finally:
        db.close()


async def get_user_subscription_status(telegram_id: int, bot) -> dict:
    """
    Главная функция проверки.

    Возвращает:
    {
        "has_access": bool,                      # подписан на всех
        "missing": [ {name, link}, ... ],        # на кого не подписан
        "rewardable": [ {task_id, name}, ... ],  # за кого можно получить награду
        "total": int,
        "subscribed_count": int,
    }
    """
    sponsors = await get_active_sponsors_with_tasks()

    if not sponsors:
        return {
            "has_access": True,
            "missing": [],
            "rewardable": [],
            "total": 0,
            "subscribed_count": 0,
        }

    # Берём completed_at для всех заданий пользователя
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=str(telegram_id)).first()
        completed_task_ids = set()
        if user:
            rows = db.query(UserTask.task_id).filter(
                UserTask.user_id == user.id,
                UserTask.completed_at.isnot(None),
            ).all()
            completed_task_ids = {str(r[0]) for r in rows}
    finally:
        db.close()

    missing = []
    rewardable = []
    subscribed_count = 0

    for sp in sponsors:
        try:
            member = await bot.get_chat_member(
                chat_id=int(sp["channel_id"]),
                user_id=int(telegram_id),
            )
            status = member.status
            is_subscribed = status in ("member", "administrator", "creator", "requested")
            print(f"   • {sp['name']} (id={sp['channel_id']}): {status}")
        except Exception as e:
            print(f"   • {sp['name']}: ERROR {e}")
            continue

        # За этого спонсора ещё не получал?
        not_yet_rewarded = sp["task_id"] and sp["task_id"] not in completed_task_ids
        if not_yet_rewarded:
            rewardable.append({"task_id": sp["task_id"], "name": sp["name"]})

        if is_subscribed:
            subscribed_count += 1
        else:
            missing.append({
                "name": sp["name"],
                "link": sp["link"],
            })

    print(f"🔍 [subscription] user={telegram_id} | "
          f"subscribed={subscribed_count}/{len(sponsors)} | "
          f"missing={len(missing)} | rewardable={len(rewardable)}")

    return {
        "has_access": len(missing) == 0,
        "missing": missing,
        "rewardable": rewardable,
        "total": len(sponsors),
        "subscribed_count": subscribed_count,
    }


# =========================================================
# 2. ВЫДАЧА НАГРАД
# =========================================================

async def grant_rewards_for_subscribed(telegram_id: int, rewardable: list[dict]) -> int:
    """
    Выдаёт билетики за каждого спонсора из rewardable,
    но только если пользователь ПОДПИСАН на канал этого спонсора.
    Помечает user_task.completed_at.
    Возвращает количество выданных билетиков.
    """
    if not rewardable:
        return 0

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=str(telegram_id)).first()
        if not user:
            print(f"⚠️ [subscription] Пользователь {telegram_id} не найден")
            return 0

        total_reward = 0

        for sp in rewardable:
            task = db.query(Task).filter_by(id=sp["task_id"]).first()
            if not task:
                continue

            user_task = db.query(UserTask).filter_by(
                user_id=user.id,
                task_id=task.id,
            ).first()

            if user_task and user_task.completed_at:
                continue

            reward = task.reward or 1
            total_reward += reward

            if not user_task:
                user_task = UserTask(
                    user_id=user.id,
                    task_id=task.id,
                    progress=1,
                    completed_at=datetime.now(),
                )
                db.add(user_task)
            else:
                user_task.completed_at = datetime.now()
                user_task.progress = 1

        if total_reward > 0:
            user.tickets += total_reward
            db.commit()
            print(f"✅ [subscription] {telegram_id} получил {total_reward} билетиков")
        else:
            print(f"ℹ️ [subscription] {telegram_id} — нечего выдавать")

        return total_reward

    except Exception as e:
        db.rollback()
        print(f"❌ [subscription] Ошибка выдачи {telegram_id}: {e}")
        return 0
    finally:
        db.close()


# =========================================================
# 3. ТЕКСТЫ И КЛАВИАТУРА ГЕЙТА
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


def get_gate_text(user_name: str, missing: list[dict], reward_amount: int) -> str:
    """
    Текст гейта.
    reward_amount — сколько билетов получит пользователь (missing + rewardable).
    Если 0 — значит, награды не будет (всё уже получал).
    """
    name = user_name or "пользователь"

    if reward_amount > 0:
        word = _pluralize(reward_amount, "прокрут", "прокрута", "прокрутов")
        return (
            f"👋 *Привет, {name}!*\n\n"
            f"Добро пожаловать в GenshinPoolBot! 🎡\n\n"
            f"Чтобы получить *{reward_amount} бесплатных {word}* и начать выбивать призы, "
            f"выполни простые шаги:\n\n"
            f"📢 *Шаг 1.* Подпишись на наших спонсоров\n"
            f"✅ *Шаг 2.* Нажми «Я подписался»\n"
            f"🎁 *Шаг 3.* Получи доступ + *{reward_amount} {word}* в подарок\n\n"
            f"👇 Жми на кнопки ниже:"
        )
    else:
        return (
            f"👋 *Привет, {name}!*\n\n"
            f"Чтобы бот снова заработал, подпишись на наших спонсоров:\n\n"
            f"📢 Подпишись на каналы ниже\n"
            f"✅ И нажми «Я подписался»\n\n"
            f"👇 Осталось подписаться: *{len(missing)}*"
        )


def get_welcome_text(user_name: str, reward: int) -> str:
    """Приветствие после успешного прохода гейта."""
    name = user_name or "пользователь"

    if reward > 0:
        word = _pluralize(reward, "прокрут", "прокрута", "прокрутов")
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
    reward_amount: int,
    context: ContextTypes.DEFAULT_TYPE | None = None,
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

    keyboard = build_subscription_gate_keyboard(missing)
    user_name = update.effective_user.first_name if update.effective_user else "пользователь"
    text = get_gate_text(user_name, missing, reward_amount)

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


# =========================================================
# 4. ОБРАБОТЧИК КНОПКИ "✅ Я ПОДПИСАЛСЯ"
# =========================================================

async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатия на '✅ Я подписался'."""
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    user_name = update.effective_user.first_name or "пользователь"

    status = await get_user_subscription_status(telegram_id, context.bot)

    if status["has_access"]:
        # Выдаём награду только за тех, на кого подписан и ещё не получал
        # (в rewardable только те, кто не получен — а подписка уже проверена выше)
        reward = await grant_rewards_for_subscribed(telegram_id, status["rewardable"])

        try:
            await query.message.delete()
        except Exception:
            pass

        from app.keyboards import get_keyboard_for_user

        await context.bot.send_message(
            chat_id=telegram_id,
            text=get_welcome_text(user_name, reward),
            parse_mode="Markdown",
            reply_markup=get_keyboard_for_user(telegram_id),
        )
    else:
        missing = status["missing"]
        reward_amount = len(status["missing"]) + len(status["rewardable"])
        keyboard = build_subscription_gate_keyboard(missing)
        text = get_gate_text(user_name, missing, reward_amount)

        try:
            await query.edit_message_text(
                text=text,
                parse_mode="Markdown",
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )
        except Exception as e:
            print(f"⚠️ [subscription] Не удалось обновить гейт: {e}")