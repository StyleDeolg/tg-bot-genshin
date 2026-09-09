from app.database import SessionLocal
from app.models.wheel import WheelConfig
import uuid

def add_prizes():
    db = SessionLocal()
    
    # Очищаем старые призы
    db.query(WheelConfig).delete()
    
    # Новые призы — ОДНА ячейка осколка
    prizes = [
        # Пусто
        {"name": "Пусто", "value": 0, "chance": 1200, "emoji": "💨", "prize_type": "empty_1"},
        {"name": "Пусто", "value": 0, "chance": 1200, "emoji": "💨", "prize_type": "empty_2"},
        {"name": "Пусто", "value": 0, "chance": 1200, "emoji": "💨", "prize_type": "empty_3"},
        {"name": "Пусто", "value": 0, "chance": 1200, "emoji": "💨", "prize_type": "empty_4"},
        
        # ОДНА ячейка осколка (базовый шанс 50%)
        {"name": "Осколок луны", "value": 0, "chance": 5000, "emoji": "🔮", "prize_type": "shard"},
        
        # Ценные призы
        {"name": "60 кристаллов", "value": 60, "chance": 100, "emoji": "💎", "prize_type": "crystals_60"},
        {"name": "Луна Genshin", "value": 0, "chance": 20, "emoji": "🌙", "prize_type": "moon"},
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
    print("✅ Призы обновлены (одна ячейка осколка)")
    print("🎯 Шансы:")
    print("   • Осколок: 50% (прогрессивно уменьшается)")
    print("   • 60 кристаллов: 1%")
    print("   • Луна: 0.2%")
    print("   • 330 кристаллов: 0.1%")

if __name__ == "__main__":
    add_prizes()