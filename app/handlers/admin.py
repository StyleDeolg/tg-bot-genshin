import os
from sqlalchemy import func
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.user import User
from app.models.wheel import WheelSpin, WheelConfig
from app.models.task import Task
from app.keyboards import get_admin_panel_keyboard, get_keyboard_for_user

ADMIN_IDS = [int(os.getenv("ADMIN_ID", "123456789"))]

def is_admin(update: Update) -> bool:
    user_id = update.effective_user.id
    return user_id in ADMIN_IDS


# ============ СТАРЫЕ АДМИН-КОМАНДЫ ============

async def add_sponsor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ У вас нет доступа")
        return
    await update.message.reply_text("🔄 Используйте админ-панель -> Добавить спонсора")

async def add_sponsor_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ У вас нет доступа")
        return
    await update.message.reply_text("🔄 Используйте админ-панель -> Добавить спонсора")

async def list_sponsors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ У вас нет доступа")
        return
    await update.message.reply_text("🔄 Используйте админ-панель -> Список спонсоров")

async def add_referral_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ У вас нет доступа")
        return
    await update.message.reply_text("🔄 Используйте админ-панель")


# ============ АДМИН-ПАНЕЛЬ ============

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Открывает админ-панель (клавиатура)"""
    if not is_admin(update):
        await update.message.reply_text("⛔ У вас нет доступа к админ-панели")
        return

    context.user_data.pop('admin_action', None)
    context.user_data.pop('target_user', None)
    context.user_data.pop('sponsor_name', None)
    context.user_data.pop('sponsors_list', None)
    
    await update.message.reply_text(
        "🛠 *Админ-панель*\n\nВыберите действие:",
        reply_markup=get_admin_panel_keyboard(),
        parse_mode="Markdown"
    )


async def admin_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выход из админ-панели"""
    user_id = update.effective_user.id
    context.user_data.pop('admin_action', None)
    context.user_data.pop('target_user', None)
    await update.message.reply_text(
        "🔙 Вы вышли из админ-панели",
        reply_markup=get_keyboard_for_user(user_id)
    )


# ============ СТАТИСТИКА ============

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    
    db = SessionLocal()
    try:
        users_count = db.query(User).count()
        spins_count = db.query(WheelSpin).count()
        donators_count = db.query(User).filter(User.is_donator == True).count()
        tasks_count = db.query(Task).count()
        
        stats = f"""
📊 *Статистика бота*

👥 Всего пользователей: {users_count}
🎡 Всего вращений: {spins_count}
👑 Донаторов: {donators_count}
📋 Заданий: {tasks_count}
        """
        await update.message.reply_text(stats, parse_mode="Markdown")
    finally:
        db.close()


# ============ ПРИЗЫ ============

async def admin_prizes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    
    db = SessionLocal()
    try:
        prizes = db.query(WheelConfig).all()
        text = "🎡 *Текущие призы:*\n\n"
        if not prizes:
            text += "❌ Призов нет\n"
        else:
            for i, p in enumerate(prizes, 1):
                text += f"{i}. {p.name} — {p.chance/100}% (шанс), {p.value} 💎\n"
        
        await update.message.reply_text(text, parse_mode="Markdown")
    finally:
        db.close()


# ============ ЗАДАНИЯ ============

async def admin_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    
    db = SessionLocal()
    try:
        tasks = db.query(Task).filter(Task.is_active == True).all()
        text = "📋 *Активные задания:*\n\n"
        if not tasks:
            text += "❌ Нет активных заданий\n"
        else:
            for i, t in enumerate(tasks, 1):
                text += f"{i}. {t.title} — {t.reward} билетов\n"
        
        await update.message.reply_text(text, parse_mode="Markdown")
    finally:
        db.close()


# ============ ВЫДАТЬ БИЛЕТЫ ============

async def admin_give_tickets_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    
    context.user_data['admin_action'] = 'give_tickets'
    await update.message.reply_text(
        "🎫 *Выдача билетов*\n\n"
        "Введите `username` или `telegram_id` и количество билетов через пробел:\n"
        "Например: `styledeolg 100` или `5646848256 50`",
        parse_mode="Markdown"
    )

async def admin_give_tickets_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    
    if context.user_data.get('admin_action') != 'give_tickets':
        return
    
    text = update.message.text.strip()
    
    if text in ["📊 Статистика", "🎡 Призы", "📋 Задания", "🎫 Выдать билеты", "📢 Рассылка", "🌙 Выдать луну", "➕ Добавить спонсора", "🗑 Удалить спонсора", "📋 Список спонсоров", "🔙 Выйти из админки", "👑 Админ-панель"]:
        context.user_data.pop('admin_action', None)
        await admin_panel(update, context)
        return
    
    parts = text.split()
    if len(parts) != 2:
        await update.message.reply_text(
            "❌ Неверный формат!\n\n"
            "Введи `username` и количество через пробел:\n"
            "Например: `styledeolg 100`",
            parse_mode="Markdown"
        )
        return
    
    user_input, amount_str = parts[0], parts[1]
    
    if user_input.startswith('@'):
        user_input = user_input[1:]
    
    db = SessionLocal()
    try:
        amount = int(amount_str)
        
        user = db.query(User).filter_by(telegram_id=user_input).first()
        if not user:
            user = db.query(User).filter(
                func.lower(User.username) == func.lower(user_input)
            ).first()
        
        if not user:
            await update.message.reply_text(
                f"❌ Пользователь с ID/username `{user_input}` не найден",
                parse_mode="Markdown"
            )
            return
        
        user.tickets += amount
        db.commit()
        
        await update.message.reply_text(
            f"✅ Пользователю `{user.username or user.telegram_id}` выдано {amount} билетов\n"
            f"Теперь у него {user.tickets} билетов",
            parse_mode="Markdown"
        )
        
        context.user_data.pop('admin_action', None)
        await admin_panel(update, context)
        
    except ValueError:
        await update.message.reply_text("❌ Введите число")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    finally:
        db.close()


# ============ РАССЫЛКА ============

async def admin_broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    
    context.user_data['admin_action'] = 'broadcast'
    await update.message.reply_text(
        "📢 *Рассылка*\n\n"
        "Введите сообщение для рассылки:",
        parse_mode="Markdown"
    )

async def admin_broadcast_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    
    action = context.user_data.get('admin_action')
    if action != 'broadcast':
        return
    
    message_text = update.message.text
    
    if message_text in ["📊 Статистика", "🎡 Призы", "📋 Задания", "🎫 Выдать билеты", "📢 Рассылка", "🌙 Выдать луну", "➕ Добавить спонсора", "🗑 Удалить спонсора", "📋 Список спонсоров", "🔙 Выйти из админки"]:
        return
    
    db = SessionLocal()
    try:
        users = db.query(User).all()
        success = 0
        failed = 0
        
        await update.message.reply_text(f"🔄 Начинаю рассылку для {len(users)} пользователей...")
        
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=int(user.telegram_id),
                    text=message_text
                )
                success += 1
            except Exception:
                failed += 1
            
            if success % 10 == 0:
                import asyncio
                await asyncio.sleep(0.5)
        
        await update.message.reply_text(
            f"✅ Рассылка завершена!\n"
            f"Успешно: {success}\n"
            f"Не доставлено: {failed}"
        )
        
        context.user_data.pop('admin_action', None)
        await admin_panel(update, context)
        
    finally:
        db.close()


# ============ ВЫДАТЬ ЛУНУ ============

async def admin_give_moon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    
    context.user_data['admin_action'] = 'give_moon'
    await update.message.reply_text(
        "🌙 *Выдача луны*\n\n"
        "Введите `username` пользователя (без @):",
        parse_mode="Markdown"
    )

async def admin_give_moon_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    
    db = SessionLocal()
    try:
        username_input = update.message.text.strip().lstrip('@')
        
        user = db.query(User).filter(
            func.lower(User.username) == func.lower(username_input)
        ).first()
        
        if not user:
            await update.message.reply_text(
                f"❌ Пользователь с username `{username_input}` не найден",
                parse_mode="Markdown"
            )
            return
        
        user.has_moon = True
        user.is_donator = True
        db.commit()
        
        from app.handlers.donator_notify import notify_donator
        await notify_donator(
            winner_telegram_id=int(user.telegram_id),
            prize="moon",
            uid=user.genshin_uid or "Не указан",
            server=user.genshin_server or "Не указан",
            username=user.username,
            first_name=user.first_name
        )
        
        await update.message.reply_text(
            f"✅ Луна выдана!\n\n"
            f"👤 Пользователь: @{user.username or user.first_name or 'Неизвестный'}\n"
            f"🆔 Telegram ID: `{user.telegram_id}`\n"
            f"📢 Уведомление отправлено донаторам.",
            parse_mode="Markdown"
        )
        
        context.user_data.pop('admin_action', None)
        await admin_panel(update, context)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    finally:
        db.close()