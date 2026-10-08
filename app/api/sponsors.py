from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.database import SessionLocal
from app.models.user import User
from app.models.sponsor import Sponsor
from app.models.task import Task, UserTask
from app.config import config
from telegram import Bot

router = APIRouter(prefix="/api/sponsors", tags=["sponsors"])

BOT_TOKEN = config.BOT_TOKEN
bot = Bot(token=BOT_TOKEN)


async def check_access_for_user(telegram_id: int) -> dict:
    """
    Проверяет доступ пользователя к боту.
    Возвращает {has_access, missing, total, subscribed_count}.
    """
    db = SessionLocal()
    try:
        sponsors = db.query(Sponsor).filter(
            Sponsor.is_active == True,
            Sponsor.channel_id.isnot(None),
        ).all()

        if not sponsors:
            return {"has_access": True, "missing": [], "total": 0, "subscribed_count": 0}

        missing = []
        subscribed_count = 0

        for sp in sponsors:
            try:
                member = await bot.get_chat_member(
                    chat_id=int(sp.channel_id),
                    user_id=int(telegram_id),
                )
                # 🔥 Разрешаем 'requested' — заявка = доступ
                if member.status in ("member", "administrator", "creator", "requested"):
                    subscribed_count += 1
                else:
                    missing.append({
                        "id": str(sp.id),
                        "name": sp.name or "Спонсор",
                        "link": sp.link,
                    })
            except Exception as e:
                print(f"⚠️ [access] Ошибка {sp.name}: {e}")
                missing.append({
                    "id": str(sp.id),
                    "name": sp.name or "Спонсор",
                    "link": sp.link,
                })

        return {
            "has_access": len(missing) == 0,
            "missing": missing,
            "total": len(sponsors),
            "subscribed_count": subscribed_count,
        }
    finally:
        db.close()


@router.get("/access/{telegram_id}")
async def check_access(telegram_id: str):
    """
    Проверка доступа в Mini App.
    Если has_access: false — фронт показывает экран подписки.
    """
    try:
        result = await check_access_for_user(int(telegram_id))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{telegram_id}")
async def get_sponsors(telegram_id: str):
    """Получить список спонсоров с статусом подписки"""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        sponsors = db.query(Sponsor).filter(Sponsor.is_active == True).all()
        
        result = []
        for sponsor in sponsors:
            task = db.query(Task).filter_by(
                sponsor_id=sponsor.id,
                is_active=True,
                task_type="sponsor"
            ).first()
            
            is_completed = False
            if task:
                user_task = db.query(UserTask).filter_by(
                    user_id=user.id,
                    task_id=task.id
                ).first()
                if user_task and user_task.completed_at:
                    is_completed = True
            
            is_subscribed = False
            if sponsor.channel_id and task and not is_completed:
                try:
                    chat_member = await bot.get_chat_member(
                        chat_id=int(sponsor.channel_id),
                        user_id=int(telegram_id)
                    )
                    # Для задачи спонсора — только реальные подписчики,
                    # но requested тоже считаем как «подписан» (заявка)
                    is_subscribed = chat_member.status in ['member', 'administrator', 'creator', 'requested']
                    print(f"✅ {sponsor.name}: {chat_member.status}")
                except Exception as e:
                    print(f"❌ {sponsor.name}: {e}")
                    is_subscribed = False
            
            result.append({
                "id": str(sponsor.id),
                "name": sponsor.name,
                "link": sponsor.link,
                "channel": sponsor.channel,
                "is_subscribed": is_subscribed,
                "task_completed": is_completed,
                "task_id": str(task.id) if task else None,
            })
        
        return result
    finally:
        db.close()


@router.post("/check/{telegram_id}/{sponsor_id}")
async def check_subscription(telegram_id: str, sponsor_id: str):
    """Проверяет подписку на канал спонсора"""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        sponsor = db.query(Sponsor).filter_by(id=sponsor_id, is_active=True).first()
        if not sponsor:
            raise HTTPException(status_code=404, detail="Спонсор не найден")
        
        if not sponsor.channel_id:
            return {
                "success": False,
                "message": "У спонсора не указан канал для проверки. Обратитесь к администратору."
            }
        
        task = db.query(Task).filter_by(
            sponsor_id=sponsor.id,
            is_active=True,
            task_type="sponsor"
        ).first()
        
        if not task:
            return {"success": False, "message": "Задание для этого спонсора не найдено"}
        
        user_task = db.query(UserTask).filter_by(
            user_id=user.id,
            task_id=task.id
        ).first()
        
        if user_task and user_task.completed_at:
            return {"success": False, "message": "Вы уже получили награду за это задание"}
        
        try:
            print(f"🔍 Проверка: пользователь {telegram_id} в канале {sponsor.channel_id}")
            
            chat_member = await bot.get_chat_member(
                chat_id=int(sponsor.channel_id),
                user_id=int(telegram_id)
            )
            
            status = chat_member.status
            print(f"📊 Статус: {status}")
            
            # Для задачи — только реальные участники
            if status not in ['member', 'administrator', 'creator']:
                return {
                    "success": False,
                    "message": "❌ Ты не подписан на канал. Подпишись и попробуй снова!"
                }
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Ошибка: {error_msg}")
            
            if "bot is not a member" in error_msg.lower():
                return {"success": False, "message": "❌ Бот не добавлен в канал как администратор!"}
            elif "user not found" in error_msg.lower():
                return {"success": False, "message": "❌ Ты не найден в канале. Подпишись и попробуй снова!"}
            else:
                return {"success": False, "message": f"❌ Ошибка проверки: {error_msg[:100]}"}
        
        reward = task.reward or 1
        user.tickets += reward
        
        if not user_task:
            user_task = UserTask(
                user_id=user.id,
                task_id=task.id,
                progress=1,
                completed_at=datetime.now()
            )
            db.add(user_task)
        else:
            user_task.completed_at = datetime.now()
            user_task.progress = 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"✅ Подписка подтверждена! Ты получил {reward} билетик! 🎉"
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()