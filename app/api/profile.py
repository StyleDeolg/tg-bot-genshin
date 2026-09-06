from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import SessionLocal
from app.models.user import User
from app.models.referral import Referral
from app.models.task import Task, UserTask

router = APIRouter(prefix="/api/profile", tags=["profile"])

class ProfileResponse(BaseModel):
    telegram_id: str
    username: str | None
    first_name: str | None
    last_name: str | None
    public_id: str
    tickets: int
    primogems: int
    genshin_uid: str | None
    genshin_server: str | None
    referrals_count: int
    tasks_completed: int
    moon_shards: int
    has_moon: bool
    is_donator: bool

@router.get("/{telegram_id}")
async def get_profile(telegram_id: str):
    db = SessionLocal()
    
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    referrals_count = db.query(Referral).filter_by(referrer_id=user.id).count()
    tasks_completed = db.query(UserTask).filter_by(
        user_id=user.id
    ).filter(UserTask.completed_at.isnot(None)).count()
    
    db.close()
    
    return ProfileResponse(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        public_id=str(user.public_id),
        tickets=user.tickets,
        primogems=user.primogems,
        genshin_uid=user.genshin_uid,
        genshin_server=user.genshin_server,
        referrals_count=referrals_count,
        tasks_completed=tasks_completed,
        moon_shards=user.moon_shards,
        has_moon=user.has_moon,
        is_donator=user.is_donator,
    )