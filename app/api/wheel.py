from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import random
from app.database import SessionLocal
from app.models.user import User
from app.models.wheel import WheelSpin, WheelConfig
from app.handlers.donator_notify import notify_donator, notify_user_win

router = APIRouter(prefix="/api/wheel", tags=["wheel"])

class SpinRequest(BaseModel):
    telegram_id: str

class SpinResponse(BaseModel):
    prize: str
    prize_value: int
    prize_type: str
    emoji: str
    tickets_left: int
    shards: int = 0
    has_moon: bool = False
    segment_index: int = 0


@router.post("/spin", response_model=SpinResponse)
async def spin(request: SpinRequest):
    db = SessionLocal()
    
    try:
        user = db.query(User).filter_by(telegram_id=request.telegram_id).first()
        if not user:
            db.close()
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        if user.tickets < 1:
            db.close()
            raise HTTPException(status_code=400, detail="Недостаточно билетиков")
        
        prizes = db.query(WheelConfig).filter_by(is_active="true").order_by(WheelConfig.created_at).all()
        if not prizes:
            db.close()
            raise HTTPException(status_code=404, detail="Призы не настроены")
        
        prizes_data = []
        for p in prizes:
            chance = p.chance
            
            # ===== ПРОГРЕССИВНЫЙ ШАНС ДЛЯ ОДНОЙ ЯЧЕЙКИ ОСКОЛКА =====
            if p.prize_type == "shard":
                # Базовый шанс 50% (5000)
                # Уменьшаем в зависимости от количества осколков
                shard_factor = max(0, 1 - (user.moon_shards / 6))
                chance = int(5000 * shard_factor)
                
                # Если шанс стал 0 — пропускаем приз
                if chance <= 0:
                    continue
            
            # Бонус для 60 кристаллов (если есть буст)
            if p.prize_type == "crystals_60" and user.crystals_60_boosted:
                chance = max(chance, 200)
            
            prizes_data.append({
                "name": str(p.name),
                "value": int(p.value),
                "chance": int(chance),
                "emoji": str(p.emoji) if p.emoji else "🎁",
                "prize_type": str(p.prize_type),
            })
        
        # Если после фильтрации не осталось призов — добавляем пустышку
        if not prizes_data:
            prizes_data = [
                {"name": "Пусто", "value": 0, "chance": 1000, "emoji": "💨", "prize_type": "empty_fallback"},
            ]
        
        total_chance = sum(p["chance"] for p in prizes_data)
        rand = random.randint(1, total_chance)
        
        cumulative = 0
        selected = prizes_data[0]
        selected_index = 0
        for idx, prize in enumerate(prizes_data):
            cumulative += prize["chance"]
            if rand <= cumulative:
                selected = prize
                selected_index = idx
                break
        
        prize_type = selected["prize_type"]
        prize_name = selected["name"]
        prize_value = selected["value"]
        prize_emoji = selected["emoji"]
        
        user.tickets -= 1
        user.spins_count += 1
        
        # Обработка выигрыша
        if prize_type == "moon":
            user.has_moon = True
            user.is_donator = True
        elif prize_type == "shard":
            user.moon_shards += 1
            if user.moon_shards >= 6:
                user.has_moon = True
                user.is_donator = True
                user.moon_shards = 0
        elif prize_type == "crystals_330":
            user.crystals_330_claimed = True
            user.is_donator = True
        elif prize_type == "crystals_60":
            user.crystals_60_claimed = True
            user.crystals_60_boosted = False
            user.is_donator = True
        elif prize_type.startswith("empty"):
            prize_value = 0
            prize_emoji = "💨"
        
        # Сохраняем спин
        spin_record = WheelSpin(
            user_id=user.id,
            prize=prize_name,
            prize_value=prize_value,
            prize_type=prize_type,
        )
        db.add(spin_record)
        db.commit()
        
        # ===== УВЕДОМЛЕНИЯ =====
        await notify_user_win(int(user.telegram_id), prize_type, user.moon_shards)
        
        if prize_type in ["moon", "crystals_60", "crystals_330"]:
            await notify_donator(
                winner_telegram_id=int(user.telegram_id),
                prize=prize_type,
                uid=user.genshin_uid or "Не указан",
                server=user.genshin_server or "Не указан",
                username=user.username,
                first_name=user.first_name
            )
        
        return SpinResponse(
            prize=prize_name,
            prize_value=prize_value,
            prize_type=prize_type,
            emoji=prize_emoji,
            tickets_left=user.tickets,
            shards=user.moon_shards or 0,
            has_moon=user.has_moon or False,
            segment_index=selected_index,
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/prizes")
async def get_prizes():
    """Получить список активных призов для колеса"""
    db = SessionLocal()
    try:
        prizes = db.query(WheelConfig).filter_by(is_active="true").order_by(WheelConfig.created_at).all()
        
        if not prizes:
            return [
                {"name": "Пусто", "value": 0, "emoji": "💨", "prize_type": "empty_1", "color": "#d4af37"},
                {"name": "Осколок луны", "value": 0, "emoji": "🔮", "prize_type": "shard", "color": "#1a1a2e"},
                {"name": "Пусто", "value": 0, "emoji": "💨", "prize_type": "empty_2", "color": "#d4af37"},
                {"name": "60 💎", "value": 60, "emoji": "💎", "prize_type": "crystals_60", "color": "#1a1a2e"},
                {"name": "Пусто", "value": 0, "emoji": "💨", "prize_type": "empty_3", "color": "#d4af37"},
                {"name": "Луна", "value": 0, "emoji": "🌙", "prize_type": "moon", "color": "#1a1a2e"},
                {"name": "Пусто", "value": 0, "emoji": "💨", "prize_type": "empty_4", "color": "#d4af37"},
                {"name": "330 💎", "value": 330, "emoji": "💎", "prize_type": "crystals_330", "color": "#1a1a2e"},
            ]
        
        return [
            {
                "name": p.name,
                "value": p.value,
                "emoji": p.emoji,
                "prize_type": p.prize_type,
                "color": i % 2 == 0 and "#d4af37" or "#1a1a2e"
            }
            for i, p in enumerate(prizes)
        ]
    finally:
        db.close()