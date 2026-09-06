import uuid
from app.database import SessionLocal
from app.models.task import Task

def add_tasks():
    db = SessionLocal()
    
    # Очищаем старые задания
    db.query(Task).delete()
    
    tasks = [
        {
            "title": "🎡 Сделать 5 спинов",
            "description": "Прокрути колесо фортуны 5 раз",
            "reward": 3,
            "task_type": "spin",
            "required_count": 5,
            "is_active": True,
            "is_repeatable": True
        },
        {
            "title": "👥 Пригласить 3 друзей",
            "description": "Пригласи 3 друзей в бота",
            "reward": 5,
            "task_type": "social",
            "required_count": 3,
            "is_active": True,
            "is_repeatable": True
        },
        {
            "title": "📅 Ежедневный бонус",
            "description": "Заходи в бота каждый день и забирай награду",
            "reward": 1,
            "task_type": "daily",
            "required_count": 1,
            "is_active": True,
            "is_repeatable": True
        },
    ]
    
    for task in tasks:
        new_task = Task(
            id=uuid.uuid4(),
            title=task["title"],
            description=task["description"],
            reward=task["reward"],
            task_type=task["task_type"],
            required_count=task["required_count"],
            is_active=task["is_active"],
            is_repeatable=task["is_repeatable"],
            sponsor_id=None
        )
        db.add(new_task)
    
    db.commit()
    db.close()
    print("✅ Задания добавлены!")

if __name__ == "__main__":
    add_tasks()