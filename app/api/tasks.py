from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.user import User
from app.models.task import Task, UserTask

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    reward: int
    task_type: str
    required_count: int
    progress: int
    completed: bool
    can_claim: bool

class ClaimResponse(BaseModel):
    success: bool
    message: str
    tickets: int

@router.get("/{telegram_id}")
async def get_tasks(telegram_id: str):
    """Получить список всех активных заданий с прогрессом пользователя"""
    db = SessionLocal()
    
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    tasks = db.query(Task).filter_by(is_active=True).all()
    result = []
    
    for task in tasks:
        user_task = db.query(UserTask).filter_by(
            user_id=user.id,
            task_id=task.id
        ).first()
        
        progress = user_task.progress if user_task else 0
        completed = user_task.completed_at is not None if user_task else False
        
        # Проверка для ежедневных заданий
        can_claim = False
        if task.task_type == "daily":
            if not user_task or not user_task.completed_at:
                can_claim = True
            elif (datetime.now() - user_task.completed_at) >= timedelta(hours=24):
                can_claim = True
        
        result.append(TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            reward=task.reward,
            task_type=task.task_type,
            required_count=task.required_count,
            progress=progress,
            completed=completed,
            can_claim=can_claim
        ))
    
    db.close()
    return result


@router.post("/claim/{telegram_id}/{task_id}")
async def claim_task(telegram_id: str, task_id: str):
    """Забрать награду за выполненное задание"""
    db = SessionLocal()
    
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    task = db.query(Task).filter_by(id=task_id, is_active=True).first()
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Задание не найдено")
    
    user_task = db.query(UserTask).filter_by(
        user_id=user.id,
        task_id=task.id
    ).first()
    
    if not user_task or not user_task.completed_at:
        db.close()
        raise HTTPException(status_code=400, detail="Задание ещё не выполнено")
    
    # Для ежедневных заданий проверяем, можно ли забрать
    if task.task_type == "daily":
        if user_task.completed_at and (datetime.now() - user_task.completed_at) < timedelta(hours=24):
            db.close()
            raise HTTPException(status_code=400, detail="Уже забрано за последние 24 часа")
    
    # Начисляем награду
    user.tickets += task.reward
    user_task.completed_at = datetime.now()
    
    db.commit()
    db.close()
    
    return ClaimResponse(
        success=True,
        message=f"Вы получили {task.reward} 🎟️ билетиков!",
        tickets=user.tickets
    )


@router.post("/check/{telegram_id}")
async def check_tasks(telegram_id: str):
    """Проверить прогресс заданий (вызывается после спина, реферала и т.д.)"""
    db = SessionLocal()
    
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Проверяем задания типа "spin"
    spin_tasks = db.query(Task).filter_by(task_type="spin", is_active=True).all()
    for task in spin_tasks:
        user_task = db.query(UserTask).filter_by(
            user_id=user.id,
            task_id=task.id
        ).first()
        
        if user_task and user_task.progress >= task.required_count and not user_task.completed_at:
            user_task.completed_at = datetime.now()
    
    # Проверяем задания типа "social" (рефералы)
    social_tasks = db.query(Task).filter_by(task_type="social", is_active=True).all()
    from app.models.referral import Referral
    for task in social_tasks:
        user_task = db.query(UserTask).filter_by(
            user_id=user.id,
            task_id=task.id
        ).first()
        
        if user_task:
            # Считаем количество рефералов
            referrals_count = db.query(Referral).filter_by(referrer_id=user.id).count()
            if referrals_count >= task.required_count and not user_task.completed_at:
                user_task.completed_at = datetime.now()
    
    db.commit()
    db.close()
    
    return {"success": True, "message": "Прогресс заданий обновлён"}