from telegram import Bot
from app.config import config

BOT_TOKEN = config.BOT_TOKEN
bot = Bot(token=BOT_TOKEN)

# Используем config.DONATOR_CHAT_IDS
DONATOR_CHAT_IDS = config.DONATOR_CHAT_IDS


async def notify_donator(winner_telegram_id: int, prize: str, uid: str, server: str, username: str, first_name: str = None):
    """Отправляет уведомление донатору о выигрыше"""

    user_display = f"@{username}" if username else first_name or str(winner_telegram_id)

    prize_names = {
        "moon": "🌙 Луна Genshin",
        "moon_from_shards": "🌙 Луна Genshin (собрана из 6 осколков)",
        "shard": "🔮 Осколок луны",
        "crystals_60": "💎 60 кристаллов",
        "crystals_330": "💎 330 кристаллов",
        "empty": "💨 Пусто",
    }
    prize_display = prize_names.get(prize, prize)

    text = (
        f"🎁 *НОВЫЙ ДОНАТ!*\n\n"
        f"👤 Победитель: {user_display}\n"
        f"🆔 Telegram ID: `{winner_telegram_id}`\n"
        f"🆔 Genshin UID: `{uid or 'Не указан'}`\n"
        f"🌍 Регион: {server or 'Не указан'}\n"
        f"🏆 Выигрыш: {prize_display}\n\n"
        f"📌 Свяжитесь с победителем и совершите донат!"
    )

    if not DONATOR_CHAT_IDS:
        print("⚠️ Список донаторов пуст! Уведомления не отправлены.")
        return

    success_count = 0
    for chat_id in DONATOR_CHAT_IDS:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown"
            )
            success_count += 1
        except Exception as e:
            print(f"❌ Ошибка отправки уведомления донатору {chat_id}: {e}")

    if success_count > 0:
        print(f"✅ Уведомление отправлено {success_count} донаторам")


async def notify_user_win(telegram_id: int, prize: str, shards: int = 0, moon_completed: bool = False):
    """
    Отправляет пользователю уведомление о выигрыше.
    
    prize: "moon" | "moon_from_shards" | "shard" | "crystals_60" | "crystals_330" | "empty..."
    shards: сколько осколков у пользователя сейчас (после операции)
    moon_completed: True, если именно в этом спине собралась луна из 6 осколков
    """

    # 🔥 Приоритет №1: луна только что собрана из осколков
    if moon_completed or prize == "moon_from_shards":
        text = (
            "🌙 *ПОЗДРАВЛЯЮ!*\n\n"
            "Ты собрал *6 осколков* и получил *ЛУНУ* в Genshin Impact! 🎉\n\n"
            "🎁 Осколки сброшены в 0.\n"
            "Скоро с тобой свяжется донатор для передачи награды."
        )
    elif prize == "moon":
        text = (
            "🌙 *ПОЗДРАВЛЯЮ!*\n\n"
            "Ты выиграл ЛУНУ в Genshin Impact! 🎉\n\n"
            "Скоро с тобой свяжется донатор для передачи награды."
        )
    elif prize == "shard":
        text = (
            "🔮 *ОСКОЛОК ЛУНЫ!*\n\n"
            f"Ты получил осколок луны! ({shards}/6)\n"
            f"Осталось собрать: *{6 - shards}*\n"
            f"Собери 6 осколков и получи ЛУНУ! 🌙"
        )
    elif prize == "crystals_60":
        text = (
            "💎 *60 КРИСТАЛЛОВ!*\n\n"
            "Ты выиграл 60 кристаллов!\n"
            "Скоро с тобой свяжется донатор для передачи награды."
        )
    elif prize == "crystals_330":
        text = (
            "💎 *330 КРИСТАЛЛОВ!*\n\n"
            "Ты выиграл 330 кристаллов!\n"
            "Скоро с тобой свяжется донатор для передачи награды."
        )
    elif prize.startswith("empty"):
        text = (
            "💨 *ПУСТО!*\n\n"
            "Тебе ничего не выпало...\n"
            "Попробуй ещё раз! 🎡"
        )
    else:
        text = f"🎁 Ты выиграл {prize}!"

    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
            parse_mode="Markdown"
        )
        print(f"✅ Уведомление отправлено пользователю {telegram_id}")
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления пользователю {telegram_id}: {e}")