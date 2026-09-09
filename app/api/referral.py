from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import SessionLocal
from app.models.user import User
from app.models.referral import Referral, ReferralReward
from app.config import config  # 👈 ИМПОРТИРУЕМ КОНФИГ

router = APIRouter(prefix="/api/referral", tags=["referral"])

class ReferralResponse(BaseModel):
    code: str
    link: str
    count: int
    rewards: list[dict]

class ReferralLinkResponse(BaseModel):
    link: str

@router.get("/{telegram_id}")
async def get_referral(telegram_id: str):
    """Получить реферальную информацию"""
    db = SessionLocal()
    
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    count = db.query(Referral).filter_by(referrer_id=user.id).count()
    rewards = db.query(ReferralReward).order_by(ReferralReward.level).all()
    
    # 🔥 ИСПОЛЬЗУЕМ КОНФИГ
    bot_username = config.BOT_USERNAME or "GenshinPool"
    link = f"https://t.me/{bot_username}?start=ref_{user.public_id}"
    
    db.close()
    
    return ReferralResponse(
        code=str(user.public_id),
        link=link,
        count=count,
        rewards=[{"level": r.level, "reward": r.reward} for r in rewards]
    )


@router.get("/link/{telegram_id}")
async def get_referral_link(telegram_id: str):
    """Получить только реферальную ссылку"""
    db = SessionLocal()
    
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # 🔥 ИСПОЛЬЗУЕМ КОНФИГ
    bot_username = config.BOT_USERNAME or "GenshinPool"
    link = f"https://t.me/{bot_username}?start=ref_{user.public_id}"
    
    db.close()
    
    return ReferralLinkResponse(link=link)


@router.get("/stats/{telegram_id}")
async def get_referral_stats(telegram_id: str):
    """Получить статистику рефералов"""
    db = SessionLocal()
    
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    total = db.query(Referral).filter_by(referrer_id=user.id).count()
    
    recent = db.query(Referral).filter_by(
        referrer_id=user.id
    ).order_by(Referral.created_at.desc()).limit(5).all()
    
    recent_list = []
    for r in recent:
        referred = db.query(User).filter_by(id=r.referred_id).first()
        recent_list.append({
            "username": referred.username if referred else "Unknown",
            "first_name": referred.first_name if referred else "Аноним",
            "date": r.created_at.strftime("%d.%m.%Y")
        })
    
    db.close()
    
    return {
        "total": total,
        "recent": recent_list,
        "next_reward": None
    }