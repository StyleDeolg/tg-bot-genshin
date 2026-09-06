import uuid
from app.database import SessionLocal
from app.models.wheel import WheelConfig

def add_prizes():
    db = SessionLocal()
    db.query(WheelConfig).delete()
    
    prizes = [
        {"name": "🌙 Луна", "value": 0, "chance": 2, "emoji": "🌙", "type": "moon"},
        {"name": "🌙 Осколок луны", "value": 1, "chance": 10, "emoji": "🌙", "type": "shard"},
        {"name": "💎 330 кристаллов", "value": 330, "chance": 5, "emoji": "💎", "type": "crystals_330"},
        {"name": "💎 60 кристаллов", "value": 60, "chance": 18, "emoji": "💎", "type": "crystals_60"},
        {"name": "✦ Пусто", "value": 0, "chance": 16, "emoji": "✦", "type": "empty"},
        {"name": "✦ Пусто", "value": 0, "chance": 16, "emoji": "✦", "type": "empty"},
        {"name": "✦ Пусто", "value": 0, "chance": 16, "emoji": "✦", "type": "empty"},
        {"name": "✦ Пусто", "value": 0, "chance": 17, "emoji": "✦", "type": "empty"},
    ]
    
    total = sum(p["chance"] for p in prizes)
    print(f"📊 Сумма шансов: {total}% {'✅' if total == 100 else '⚠️'}")
    
    for prize in prizes:
        new_prize = WheelConfig(
            id=uuid.uuid4(),
            name=prize["name"],
            value=prize["value"],
            chance=prize["chance"],
            emoji=prize["emoji"],
            is_active="true",
            prize_type=prize["type"],
        )
        db.add(new_prize)
    
    db.commit()
    db.close()
    print("✅ Призы для колеса обновлены!")

if __name__ == "__main__":
    add_prizes()