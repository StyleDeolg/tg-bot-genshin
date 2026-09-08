from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models.user import User

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.get("/{telegram_id}")
async def get_profile(telegram_id: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Считаем количество выполненных заданий
        tasks_completed = 0
        if user.user_tasks:
            tasks_completed = sum(1 for ut in user.user_tasks if ut.completed_at)
        
        # Считаем рефералов
        referrals_count = 0
        if hasattr(user, 'referrals_given'):
            referrals_count = len(user.referrals_given)
        
        return {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "tickets": user.tickets,
            "moon_shards": user.moon_shards,  # ← ТОЛЬКО осколки
            "is_donator": user.is_donator,
            "genshin_uid": user.genshin_uid,
            "genshin_server": user.genshin_server,
            "referrals_count": referrals_count,
            "tasks_completed": tasks_completed,
        }
    finally:
        db.close()