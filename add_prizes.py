from app.database import SessionLocal
from app.models.wheel import WheelConfig
import uuid

def fix_prizes():
    db = SessionLocal()
    
    # Удаляем старые призы
    db.query(WheelConfig).delete()
    
    # Правильный порядок (как на колесе):
    # 0: Пусто
    # 1: Осколок луны
    # 2: Пусто
    # 3: 60 кристаллов
    # 4: Пусто
    # 5: Луна
    # 6: Пусто
    # 7: 330 кристаллов
    prizes = [
        {"name": "Пусто", "value": 0, "chance": 1206, "emoji": "💨", "prize_type": "empty_1"},
        {"name": "Осколок луны", "value": 0, "chance": 180, "emoji": "🔮", "prize_type": "shard"},
        {"name": "Пусто", "value": 0, "chance": 1206, "emoji": "💨", "prize_type": "empty_2"},
        {"name": "60 кристаллов", "value": 60, "chance": 100, "emoji": "💎", "prize_type": "crystals_60"},
        {"name": "Пусто", "value": 0, "chance": 1206, "emoji": "💨", "prize_type": "empty_3"},
        {"name": "Луна Genshin", "value": 0, "chance": 20, "emoji": "🌙", "prize_type": "moon"},
        {"name": "Пусто", "value": 0, "chance": 1207, "emoji": "💨", "prize_type": "empty_4"},
        {"name": "330 кристаллов", "value": 330, "chance": 50, "emoji": "💎", "prize_type": "crystals_330"},
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
    fix_prizes()