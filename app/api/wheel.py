from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import random
from app.database import SessionLocal
from app.models.user import User
from app.models.wheel import WheelSpin, WheelConfig
from app.models.task import Task, UserTask
from app.models.leaderboard import LeaderboardEntry

router = APIRouter(prefix="/api/wheel", tags=["wheel"])

class SpinRequest(BaseModel):
    telegram_id: str

class SpinResponse(BaseModel):
    prize: str
    prize_value: int
    emoji: str
    tickets_left: int
    primogems: int
    prize_type: str
    shards: int
    has_moon: bool

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
        
        # Получаем призы
        prizes = db.query(WheelConfig).filter_by(is_active="true").all()
        if not prizes:
            db.close()
            raise HTTPException(status_code=404, detail="Призы не настроены")
        
        # --- ЛОГИКА ШАНСОВ С БУСТОМ НА 60 КРИСТАЛЛОВ ---
        prizes_data = []
        for p in prizes:
            chance = p.chance
            
            # Если 60 кристаллов и пользователь ещё не получал их — бустим шанс до 20%
            if p.prize_type == "crystals_60" and user.crystals_60_boosted:
                chance = 200  # 20% в промилле
            
            prizes_data.append({
                "name": str(p.name),
                "value": int(p.value),
                "chance": int(chance),
                "emoji": str(p.emoji) if p.emoji else "🎁",
                "type": str(p.prize_type),
            })
        
        # Выбираем приз
        total_chance = sum(p["chance"] for p in prizes_data)
        rand = random.randint(1, total_chance)
        
        cumulative = 0
        selected = prizes_data[0]
        for prize in prizes_data:
            cumulative += prize["chance"]
            if rand <= cumulative:
                selected = prize
                break
        
        # Списываем билетик
        user.tickets -= 1
        
        # --- ОБРАБОТКА ВЫИГРЫША ---
        prize_type = selected["type"]
        prize_name = selected["name"]
        prize_value = selected["value"]
        prize_emoji = selected["emoji"]
        
        shards = user.moon_shards
        has_moon = user.has_moon
        
        # 1. ЛУНА
        if prize_type == "moon":
            user.has_moon = True
            user.is_donator = True
            # Отправляем уведомление донатчику (TODO)
        
        # 2. ОСКОЛОК ЛУНЫ
        elif prize_type == "shard":
            user.moon_shards += 1
            if user.moon_shards >= 6:
                user.has_moon = True
                user.is_donator = True
                user.moon_shards = 0
                # Отправляем уведомление донатчику (TODO)
        
        # 3. 330 КРИСТАЛЛОВ
        elif prize_type == "crystals_330":
            user.crystals_330_claimed = True
            user.is_donator = True
            # Отправляем уведомление донатчику (TODO)
        
        # 4. 60 КРИСТАЛЛОВ
        elif prize_type == "crystals_60":
            user.crystals_60_claimed = True
            user.crystals_60_boosted = False
            user.is_donator = True
            # Отправляем уведомление донатчику (TODO)
        
        # 5. ПУСТО
        else:
            prize_value = 0
        
        # Сохраняем спин
        spin_record = WheelSpin(
            user_id=user.id,
            prize=prize_name,
            prize_value=prize_value,
            prize_type=prize_type,
        )
        db.add(spin_record)
        
        db.commit()
        
        return SpinResponse(
            prize=prize_name,
            prize_value=prize_value,
            emoji=prize_emoji,
            tickets_left=user.tickets,
            primogems=user.primogems,
            prize_type=prize_type,
            shards=user.moon_shards,
            has_moon=user.has_moon,
        )
        
    except Exception as e:
        db.rollback()
        db.close()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prizes")
async def get_prizes():
    """Получить список активных призов для колеса"""
    db = SessionLocal()
    prizes = db.query(WheelConfig).filter_by(is_active="true").all()
    db.close()
    
    return [
        {
            "name": p.name,
            "value": p.value,
            "emoji": p.emoji,
            "color": i % 2 == 0 and "#d4af37" or "#1a1a2e"
        }
        for i, p in enumerate(prizes)
    ]