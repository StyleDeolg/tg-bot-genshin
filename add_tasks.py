import uuid
from app.database import SessionLocal
from app.models.task import Task

def add_tasks():
    db = SessionLocal()
    
    # Очищаем старые задания
    db.query(Task).delete()
    
    tasks = [
        # 1. ЕЖЕДНЕВНОЕ (цикличное)
        {
            "title": "📅 Ежедневный бонус",
            "description": "Заходи в бота каждый день и забирай награду!",
            "reward": 1,
            "task_type": "daily",
            "required_count": 1,
            "is_active": True,
            "is_repeatable": True,
            "sponsor_id": None
        },
        # 2. ЗАДАНИЕ НА СПИНЫ (цикличное) — 5 спинов = 1 билетик
        {
            "title": "🎡 Сделать 5 спинов",
            "description": "Прокрути колесо фортуны 5 раз",
            "reward": 1,  # 🔥 ИСПРАВЛЕНО: 3 → 1
            "task_type": "spin",
            "required_count": 5,
            "is_active": True,
            "is_repeatable": True,
            "sponsor_id": None
        },
        # 3. СОЦИАЛЬНОЕ ЗАДАНИЕ (рефералы, цикличное) — 3 друга = 1 билетик
        {
            "title": "👥 Пригласить 3 друзей",
            "description": "Пригласи 3 друзей в бота",
            "reward": 1,  # 🔥 ИСПРАВЛЕНО: 3 → 1
            "task_type": "social",
            "required_count": 3,
            "is_active": True,
            "is_repeatable": True,
            "sponsor_id": None
        },
    ]
    
    for task_data in tasks:
        new_task = Task(
            id=uuid.uuid4(),
            title=task_data["title"],
            description=task_data["description"],
            reward=task_data["reward"],
            task_type=task_data["task_type"],
            required_count=task_data["required_count"],
            is_active=task_data["is_active"],
            is_repeatable=task_data["is_repeatable"],
            sponsor_id=task_data["sponsor_id"]
        )
        db.add(new_task)
    
    db.commit()
    db.close()
    print("✅ Задания добавлены!")
    print("")
    print("📋 Список заданий:")
    for task_data in tasks:
        print(f"   • {task_data['title']} — {task_data['reward']} билетов")
    print("")
    print("🔄 Цикличные задания:")
    print("   • Спины — сбрасываются после получения награды")
    print("   • Друзья — сбрасываются после получения награды")

if __name__ == "__main__":
    add_tasks()