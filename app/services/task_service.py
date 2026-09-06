from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.task import Task, UserTask
from app.models.user import User


class TaskService:

    @staticmethod
    def check_and_update_task(user_id: str, task_type: str, progress_increment: int = 1, sponsor_id: str = None):
        """Обновляет прогресс заданий определённого типа"""
        db = SessionLocal()
        
        query = db.query(Task).filter_by(task_type=task_type, is_active=True)
        if sponsor_id:
            query = query.filter_by(sponsor_id=sponsor_id)
        
        tasks = query.all()
        
        for task in tasks:
            user_task = db.query(UserTask).filter_by(
                user_id=user_id,
                task_id=task.id
            ).first()
            
            if task.task_type == "daily" and user_task:
                if user_task.completed_at and (datetime.now() - user_task.completed_at) < timedelta(hours=24):
                    continue
            
            if not user_task:
                user_task = UserTask(
                    user_id=user_id,
                    task_id=task.id,
                    progress=0
                )
                db.add(user_task)
            
            if task.task_type == "sponsor" and user_task.completed_at:
                continue
            
            user_task.progress += progress_increment
            
            if user_task.progress >= task.required_count and not user_task.completed_at:
                user_task.completed_at = datetime.now()
                user = db.query(User).filter_by(id=user_id).first()
                if user:
                    user.tickets += task.reward
                    db.commit()
        
        db.commit()
        db.close()

    @staticmethod
    def claim_daily_reward(user_id: str) -> bool:
        """Забирает ежедневную награду"""
        db = SessionLocal()
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            db.close()
            return False
        
        daily_tasks = db.query(Task).filter_by(task_type="daily", is_active=True).all()
        for task in daily_tasks:
            user_task = db.query(UserTask).filter_by(
                user_id=user_id,
                task_id=task.id
            ).first()
            
            if user_task and user_task.completed_at:
                if (datetime.now() - user_task.completed_at) < timedelta(hours=24):
                    continue
            
            user.tickets += task.reward
            if not user_task:
                user_task = UserTask(
                    user_id=user_id,
                    task_id=task.id,
                    progress=1,
                    completed_at=datetime.now()
                )
                db.add(user_task)
            else:
                user_task.completed_at = datetime.now()
            db.commit()
            db.close()
            return True
        
        db.close()
        return False

    @staticmethod
    def get_user_tasks(user_id: str):
        """Возвращает все задания пользователя с прогрессом"""
        db = SessionLocal()
        tasks = db.query(Task).filter_by(is_active=True).all()
        result = []
        
        for task in tasks:
            user_task = db.query(UserTask).filter_by(
                user_id=user_id,
                task_id=task.id
            ).first()
            
            result.append({
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "reward": task.reward,
                "task_type": task.task_type,
                "required_count": task.required_count,
                "progress": user_task.progress if user_task else 0,
                "completed": user_task.completed_at is not None if user_task else False,
                "can_claim": task.task_type == "daily" and (
                    not user_task or 
                    not user_task.completed_at or 
                    (datetime.now() - user_task.completed_at) >= timedelta(hours=24)
                )
            })
        
        db.close()
        return result