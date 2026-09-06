import uuid
from app.database import SessionLocal
from app.models.referral import ReferralReward

def add_rewards():
    db = SessionLocal()
    
    # Очищаем старые награды
    db.query(ReferralReward).delete()
    
    rewards = [
        {"level": 1, "reward": 1},   # за 1 друга — 1 билетик
        {"level": 3, "reward": 2},   # за 3 друзей — 2 билетика
        {"level": 5, "reward": 3},   # за 5 друзей — 3 билетика
        {"level": 10, "reward": 4},  # за 10 друзей — 4 билетика
        {"level": 20, "reward": 8},  # за 20 друзей — 8 билетиков
    ]
    
    for r in rewards:
        reward = ReferralReward(
            id=uuid.uuid4(),
            level=r["level"],
            reward=r["reward"]
        )
        db.add(reward)
    
    db.commit()
    db.close()
    print("✅ Награды за рефералов обновлены!")

if __name__ == "__main__":
    add_rewards()