from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models.user import User
from app.models.sponsor import Sponsor
from app.config import config
from telegram import Bot

router = APIRouter(prefix="/api/sponsors", tags=["sponsors"])

BOT_TOKEN = config.BOT_TOKEN
bot = Bot(token=BOT_TOKEN)


@router.get("/access/{telegram_id}")
async def check_access(telegram_id: str):
    """
    Проверка доступа для Mini App.
    Учитывает:
    - реальную подписку через get_chat_member
    - клики в боте (clicked_sponsors в БД)
    - флаг skip_subscription_check (старые пользователи)
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(telegram_id=str(telegram_id)).first()
        if not user:
            return {
                "has_access": False,
                "missing": [],
                "total": 0,
                "subscribed_count": 0,
                "is_old": False,
            }

        # 🔥 Старый пользователь — пропуск
        if user.skip_subscription_check:
            return {
                "has_access": True,
                "missing": [],
                "total": 0,
                "subscribed_count": 0,
                "is_old": True,
            }

        # Спонсоры
        sponsors = db.query(Sponsor).filter(
            Sponsor.is_active == True,
            Sponsor.channel_id.isnot(None),
        ).all()

        if not sponsors:
            return {
                "has_access": True,
                "missing": [],
                "total": 0,
                "subscribed_count": 0,
                "is_old": False,
            }

        # Клики из БД
        clicked = list(user.clicked_sponsors or [])

        missing = []
        subscribed_count = 0

        for sp in sponsors:
            sp_id = str(sp.id)

            # Реально подписан?
            is_subscribed = False
            try:
                member = await bot.get_chat_member(
                    chat_id=int(sp.channel_id),
                    user_id=int(telegram_id),
                )
                if member.status in ("member", "administrator", "creator", "requested"):
                    is_subscribed = True
            except Exception as e:
                print(f"⚠️ [access] Ошибка проверки {sp.name}: {e}")

            # Пройден, если подписан ИЛИ кликнул
            is_passed = is_subscribed or (sp_id in clicked)

            if is_passed:
                subscribed_count += 1
            else:
                missing.append({
                    "id": sp_id,
                    "name": sp.name or "Спонсор",
                    "link": sp.link,
                })

        return {
            "has_access": len(missing) == 0,
            "missing": missing,
            "total": len(sponsors),
            "subscribed_count": subscribed_count,
            "is_old": False,
        }

    finally:
        db.close()


@router.get("/{telegram_id}")
async def get_sponsors_legacy(telegram_id: str):
    """Заглушка для обратной совместимости (фронт это не использует)."""
    return []