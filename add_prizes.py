from app.database import SessionLocal
from app.models.wheel import WheelConfig
import uuid

def add_prizes():
    db = SessionLocal()
    
    # Очищаем старые призы
    db.query(WheelConfig).delete()
    
    # Правильный порядок с полем order
    prizes = [
        {"name": "Пусто", "value": 0, "chance": 1200, "emoji": "💨", "prize_type": "empty_1", "order": 0},
        {"name": "Осколок луны", "value": 0, "chance": 5000, "emoji": "🔮", "prize_type": "shard", "order": 1},
        {"name": "Пусто", "value": 0, "chance": 1200, "emoji": "💨", "prize_type": "empty_2", "order": 2},
        {"name": "60 кристаллов", "value": 60, "chance": 100, "emoji": "💎", "prize_type": "crystals_60", "order": 3},
        {"name": "Пусто", "value": 0, "chance": 1200, "emoji": "💨", "prize_type": "empty_3", "order": 4},
        {"name": "Луна Genshin", "value": 0, "chance": 20, "emoji": "🌙", "prize_type": "moon", "order": 5},
        {"name": "Пусто", "value": 0, "chance": 1200, "emoji": "💨", "prize_type": "empty_4", "order": 6},
        {"name": "330 кристаллов", "value": 330, "chance": 10, "emoji": "💎", "prize_type": "crystals_330", "order": 7},
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
            order=p["order"],
        )
        db.add(prize)
    
    db.commit()
    db.close()
    print("✅ Призы обновлены!")
    print("")
    print("🎡 Порядок на колесе:")
    for p in prizes:
        print(f"   {p['order']}: {p['name']}")

if __name__ == "__main__":
    add_prizes()