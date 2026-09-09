from app.database import SessionLocal
from app.models.wheel import WheelConfig
import uuid

def add_prizes():
    db = SessionLocal()
    
    # Очищаем старые призы
    db.query(WheelConfig).delete()
    
    # ПРАВИЛЬНЫЙ ПОРЯДОК (индексы 0-7)
    prizes = [
        {"name": "Пусто", "value": 0, "chance": 1200, "emoji": "💨", "prize_type": "empty_1"},
        {"name": "Осколок луны", "value": 0, "chance": 5000, "emoji": "🔮", "prize_type": "shard"},
        {"name": "Пусто", "value": 0, "chance": 1200, "emoji": "💨", "prize_type": "empty_2"},
        {"name": "60 кристаллов", "value": 60, "chance": 100, "emoji": "💎", "prize_type": "crystals_60"},
        {"name": "Пусто", "value": 0, "chance": 1200, "emoji": "💨", "prize_type": "empty_3"},
        {"name": "Луна Genshin", "value": 0, "chance": 20, "emoji": "🌙", "prize_type": "moon"},
        {"name": "Пусто", "value": 0, "chance": 1200, "emoji": "💨", "prize_type": "empty_4"},
        {"name": "330 кристаллов", "value": 330, "chance": 10, "emoji": "💎", "prize_type": "crystals_330"},
    ]
    
    for p in prizes:
        prize = WheelConfig(
            id=uuid.uuid4(),
            name=p["name"],
            value=p["value"],
            chance=p["chance"],
            emoji=p["emoji"],
            is_active="true",
            prize_type=p["prize_type"],
        )
        db.add(prize)
    
    db.commit()
    db.close()
    print("✅ Призы обновлены в правильном порядке!")

if __name__ == "__main__":
    add_prizes()