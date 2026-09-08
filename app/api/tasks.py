from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.user import User
from app.models.task import Task, UserTask
from app.models.referral import Referral

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
    sponsor_id: str | None = None
    last_claimed_at: str | None = None


class ClaimResponse(BaseModel):
    success: bool
    message: str
    tickets: int


@router.get("/{telegram_id}")
async def get_tasks(telegram_id: str):
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
        
        if not user_task:
            user_task = UserTask(
                user_id=user.id,
                task_id=task.id,
                progress=0
            )
            db.add(user_task)
            db.flush()
        
        if task.task_type == "spin":
            progress = user.spins_count
            completed = progress >= task.required_count and user_task.completed_at is not None
        else:
            progress = user_task.progress
            completed = user_task.completed_at is not None
        
        can_claim = False
        last_claimed_at = None
        
        if task.task_type == "daily":
            if user_task.last_claimed_at:
                time_diff = datetime.now() - user_task.last_claimed_at
                if time_diff >= timedelta(hours=24):
                    can_claim = True
                last_claimed_at = user_task.last_claimed_at.isoformat()
            else:
                can_claim = True
        else:
            if task.task_type == "spin":
                if user.spins_count >= task.required_count and not user_task.claimed_at:
                    can_claim = True
            elif completed and not user_task.claimed_at:
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
            can_claim=can_claim,
            sponsor_id=str(task.sponsor_id) if task.sponsor_id else None,
            last_claimed_at=last_claimed_at,
        ))
    
    db.commit()
    db.close()
    return result


@router.post("/claim/{telegram_id}/{task_id}")
async def claim_task(telegram_id: str, task_id: str):
    db = SessionLocal()
    
    try:
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
        
        if not user_task:
            db.close()
            raise HTTPException(status_code=400, detail="Задание не начато")
        
        # ===== ЕЖЕДНЕВНОЕ ЗАДАНИЕ =====
        if task.task_type == "daily":
            if user_task.last_claimed_at:
                time_diff = datetime.now() - user_task.last_claimed_at
                if time_diff < timedelta(hours=24):
                    db.close()
                    raise HTTPException(status_code=400, detail="Можно забирать раз в 24 часа")
            
            user_task.last_claimed_at = datetime.now()
            user_task.completed_at = datetime.now()
            user_task.progress = 1
            
        # ===== ЗАДАНИЕ НА СПИНЫ =====
        elif task.task_type == "spin":
            if user.spins_count < task.required_count:
                db.close()
                raise HTTPException(status_code=400, detail="Задание ещё не выполнено")
            
            if user_task.claimed_at:
                db.close()
                raise HTTPException(status_code=400, detail="Награда уже получена")
            
            user.spins_count = 0
            user_task.claimed_at = datetime.now()
            user_task.completed_at = datetime.now()
            
        # ===== ОСТАЛЬНЫЕ =====
        else:
            if not user_task.completed_at:
                db.close()
                raise HTTPException(status_code=400, detail="Задание ещё не выполнено")
            
            if user_task.claimed_at:
                db.close()
                raise HTTPException(status_code=400, detail="Награда уже получена")
            
            user_task.claimed_at = datetime.now()
        
        # Начисляем награду
        user.tickets += task.reward
        db.commit()
        
        return ClaimResponse(
            success=True,
            message=f"Вы получили {task.reward} 🎟️ билетиков!",
            tickets=user.tickets
        )
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка в claim_task: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/check/{telegram_id}")
async def check_tasks(telegram_id: str):
    db = SessionLocal()
    
    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # ===== SPIN =====
    spin_tasks = db.query(Task).filter_by(task_type="spin", is_active=True).all()
    for task in spin_tasks:
        user_task = db.query(UserTask).filter_by(
            user_id=user.id,
            task_id=task.id
        ).first()
        
        if not user_task:
            user_task = UserTask(
                user_id=user.id,
                task_id=task.id,
                progress=0
            )
            db.add(user_task)
            db.flush()
        
        if user.spins_count >= task.required_count and not user_task.completed_at:
            user_task.completed_at = datetime.now()
    
    # ===== SOCIAL =====
    social_tasks = db.query(Task).filter_by(task_type="social", is_active=True).all()
    for task in social_tasks:
        user_task = db.query(UserTask).filter_by(
            user_id=user.id,
            task_id=task.id
        ).first()
        
        if not user_task:
            user_task = UserTask(
                user_id=user.id,
                task_id=task.id,
                progress=0
            )
            db.add(user_task)
            db.flush()
        
        if not user_task.completed_at:
            referrals_count = db.query(Referral).filter_by(referrer_id=user.id).count()
            user_task.progress = referrals_count
            
            if user_task.progress >= task.required_count:
                user_task.completed_at = datetime.now()
    
    db.commit()
    db.close()
    
    return {"success": True, "message": "Прогресс заданий обновлён"}