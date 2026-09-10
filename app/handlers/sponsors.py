import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.sponsor import Sponsor
from app.models.task import Task
from app.keyboards import get_admin_panel_keyboard
from app.config import config


def is_admin(update: Update) -> bool:
    user_id = update.effective_user.id
    return user_id in config.ADMIN_IDS


# ============ ДОБАВЛЕНИЕ СПОНСОРА (РУЧНАЯ ОБРАБОТКА) ============

async def add_sponsor_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс добавления спонсора"""
    if not is_admin(update):
        return
    
    # Устанавливаем состояние
    context.user_data['add_sponsor_step'] = 'name'
    context.user_data['waiting_for_sponsor'] = True
    
    await update.message.reply_text(
        "➕ *Добавление спонсора*\n\n"
        "Введите название спонсора:",
        parse_mode="Markdown"
    )


async def add_sponsor_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод данных для спонсора"""
    if not is_admin(update):
        return
    
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Если пользователь нажал "Отмена"
    if text == "❌ Отмена":
        context.user_data.clear()
        await update.message.reply_text(
            "❌ Добавление спонсора отменено.",
            reply_markup=get_admin_panel_keyboard()
        )
        return
    
    step = context.user_data.get('add_sponsor_step')
    
    # Шаг 1: Название спонсора
    if step == 'name':
        context.user_data['sponsor_name'] = text
        context.user_data['add_sponsor_step'] = 'link'
        await update.message.reply_text(
            "Введите ссылку на канал или чат (например, https://t.me/username):"
        )
    
    # Шаг 2: Ссылка на канал
    elif step == 'link':
        context.user_data['sponsor_link'] = text
        context.user_data['add_sponsor_step'] = 'channel_id'
        
        # Извлекаем @username из ссылки
        channel = None
        if 't.me/' in text:
            match = re.search(r't\.me/([^/?]+)', text)
            if match:
                channel = f"@{match.group(1)}"
        context.user_data['sponsor_channel'] = channel
        
        await update.message.reply_text(
            "📢 *Введите ID канала*\n\n"
            "Как получить ID канала (проверенные боты):\n\n"
            "1️⃣ *@getmyid_bot* — самый простой\n"
            "   → Отправь боту любое сообщение из канала\n"
            "   → Он ответит ID\n\n"
            "2️⃣ *@chatIDrobot* — альтернативный\n"
            "   → Добавь бота в канал\n"
            "   → Напиши /start в канале\n"
            "   → Он ответит ID\n\n"
            "3️⃣ *@username_to_id_bot* — по @username\n"
            "   → Отправь @username канала\n"
            "   → Получишь ID\n\n"
            "📝 Пример ID: `-1001234567890`\n"
            "📝 Или просто отправь @username канала\n\n"
            "⚠️ Бот должен быть администратором канала для проверки подписки!",
            parse_mode="Markdown"
        )
    
    # Шаг 3: ID канала
    elif step == 'channel_id':
        channel_id = None
        channel = context.user_data.get('sponsor_channel')
        
        # Пробуем определить, что ввёл пользователь
        if text.startswith('@'):
            # Это username канала
            channel = text
            try:
                chat = await context.bot.get_chat(chat_id=text)
                channel_id = chat.id
                await update.message.reply_text(
                    f"✅ Найден канал: *{chat.title or text}*\n"
                    f"🆔 ID: `{channel_id}`",
                    parse_mode="Markdown"
                )
            except Exception as e:
                await update.message.reply_text(
                    f"❌ Не удалось найти канал по username `{text}`.\n\n"
                    f"Убедись, что:\n"
                    f"1. Бот добавлен в канал\n"
                    f"2. У канала есть @username\n"
                    f"3. Бот является администратором\n\n"
                    f"Используй @getmyid_bot для получения ID.",
                    parse_mode="Markdown"
                )
                return
        else:
            # Пробуем как числовой ID
            try:
                channel_id = int(text)
                await update.message.reply_text(
                    f"✅ ID канала принят: `{channel_id}`",
                    parse_mode="Markdown"
                )
            except ValueError:
                await update.message.reply_text(
                    "❌ Неверный формат!\n\n"
                    "Введи:\n"
                    "• `-1001234567890` — числовой ID канала\n"
                    "• `@username` — @username канала\n\n"
                    "Или используй @getmyid_bot для получения ID.",
                    parse_mode="Markdown"
                )
                return
        
        # Проверяем, может ли бот проверять подписку
        if channel_id:
            try:
                bot_member = await context.bot.get_chat_member(
                    chat_id=channel_id,
                    user_id=context.bot.id
                )
                
                if bot_member.status in ['administrator', 'creator']:
                    await update.message.reply_text(
                        "✅ Бот является администратором канала!",
                        parse_mode="Markdown"
                    )
                else:
                    await update.message.reply_text(
                        "⚠️ Бот НЕ является администратором канала!\n\n"
                        "Добавь бота в канал как администратора, иначе проверка не сработает.",
                        parse_mode="Markdown"
                    )
            except Exception as e:
                await update.message.reply_text(
                    f"⚠️ Не удалось проверить статус бота.\n"
                    f"Убедись, что бот добавлен в канал как администратор.\n\n"
                    f"Ошибка: {str(e)[:100]}",
                    parse_mode="Markdown"
                )
        
        # ===== СОЗДАЁМ СПОНСОРА =====
        name = context.user_data.get('sponsor_name')
        link = context.user_data.get('sponsor_link')
        
        db = SessionLocal()
        try:
            sponsor = Sponsor(
                name=name,
                link=link,
                channel=channel,
                channel_id=channel_id,
                is_active=True
            )
            db.add(sponsor)
            db.flush()
            
            # Создаём задание для подписки
            task = Task(
                title=f"Подпишись на {name}",
                description=f"Подпишись на канал {name} и получи 1 билетик!",
                reward=1,
                task_type="sponsor",
                required_count=1,
                is_active=True,
                is_repeatable=False,
                sponsor_id=sponsor.id
            )
            db.add(task)
            db.commit()
            
            await update.message.reply_text(
                f"✅ *Спонсор добавлен!*\n\n"
                f"📌 Название: *{name}*\n"
                f"🔗 Ссылка: {link}\n"
                f"📢 Канал: {channel or 'не указан'}\n"
                f"🆔 ID канала: `{channel_id or 'не указан'}`\n"
                f"📋 Задание создано!\n\n"
                f"⚠️ Чтобы проверка работала, бот должен быть администратором канала!",
                parse_mode="Markdown",
                reply_markup=get_admin_panel_keyboard()
            )
            
            # Очищаем состояние
            context.user_data.clear()
            
        except Exception as e:
            db.rollback()
            await update.message.reply_text(f"❌ Ошибка: {e}")
        finally:
            db.close()


# ============ УДАЛЕНИЕ СПОНСОРА ============

async def delete_sponsor_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начинает процесс удаления спонсора"""
    if not is_admin(update):
        return
    
    db = SessionLocal()
    try:
        sponsors = db.query(Sponsor).filter(Sponsor.is_active == True).all()
        if not sponsors:
            await update.message.reply_text("❌ Активных спонсоров нет")
            return
        
        text = "🗑 *Удаление спонсора*\n\nВыберите спонсора для удаления:\n"
        for i, s in enumerate(sponsors, 1):
            text += f"{i}. {s.name} — {s.channel or 'без канала'}\n"
        
        text += "\nВведите номер спонсора для удаления:"
        
        context.user_data['admin_action'] = 'delete_sponsor'
        context.user_data['sponsors_list'] = sponsors
        await update.message.reply_text(text, parse_mode="Markdown")
        
    finally:
        db.close()


async def delete_sponsor_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаляет спонсора по номеру"""
    try:
        index = int(update.message.text) - 1
        sponsors = context.user_data.get('sponsors_list', [])
        
        if index < 0 or index >= len(sponsors):
            await update.message.reply_text("❌ Неверный номер. Попробуйте снова:")
            return
        
        sponsor = sponsors[index]
        
        db = SessionLocal()
        try:
            sponsor.is_active = False
            db.commit()
            
            task = db.query(Task).filter_by(sponsor_id=sponsor.id).first()
            if task:
                task.is_active = False
                db.commit()
            
            await update.message.reply_text(
                f"✅ Спонсор *{sponsor.name}* удален!\n"
                f"📋 Связанное задание деактивировано.",
                parse_mode="Markdown",
                reply_markup=get_admin_panel_keyboard()
            )
            
        finally:
            db.close()
            
    except ValueError:
        await update.message.reply_text("❌ Введите номер")
        return
    
    context.user_data.pop('admin_action', None)
    context.user_data.pop('sponsors_list', None)


# ============ СПИСОК СПОНСОРОВ ============

async def list_sponsors_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список активных спонсоров"""
    if not is_admin(update):
        return
    
    db = SessionLocal()
    try:
        sponsors = db.query(Sponsor).filter(Sponsor.is_active == True).all()
        
        if not sponsors:
            await update.message.reply_text("❌ Активных спонсоров нет")
            return
        
        text = "📋 *Список спонсоров:*\n\n"
        for i, s in enumerate(sponsors, 1):
            text += f"{i}. *{s.name}*\n"
            text += f"   🔗 {s.link}\n"
            text += f"   📢 {s.channel or 'без канала'}\n"
            text += f"   🆔 `{s.channel_id}`\n\n"
        
        await update.message.reply_text(text, parse_mode="Markdown")
        
    finally:
        db.close()