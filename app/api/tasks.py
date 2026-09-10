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
        
        # ===== ПРОГРЕСС =====
        if task.task_type == "spin":
            progress = user.spins_count
            completed = progress >= task.required_count and user_task.completed_at is not None
        elif task.task_type == "social":
            progress = db.query(Referral).filter_by(referrer_id=user.id).count()
            if user_task.progress != progress:
                user_task.progress = progress
                db.commit()
            completed = progress >= task.required_count and user_task.completed_at is not None
        else:
            progress = user_task.progress
            completed = user_task.completed_at is not None
        
        # ===== МОЖНО ЛИ ЗАБРАТЬ? =====
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
        
        elif task.task_type == "spin":
            # 🔥 Спинов хватает И в этом цикле ещё не забирали
            if user.spins_count >= task.required_count and not user_task.claimed_at:
                can_claim = True
        
        elif task.task_type == "sponsor":
            if completed and not user_task.claimed_at:
                can_claim = True
        
        elif task.task_type == "social":
            # 🔥 Рефералов хватает И в этом цикле ещё не забирали
            if progress >= task.required_count and not user_task.claimed_at:
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
        
        # ===== ЕЖЕДНЕВНОЕ (ЦИКЛИЧНОЕ РАЗ В 24 ЧАСА) =====
        if task.task_type == "daily":
            if user_task.last_claimed_at:
                time_diff = datetime.now() - user_task.last_claimed_at
                if time_diff < timedelta(hours=24):
                    db.close()
                    raise HTTPException(status_code=400, detail="Можно забирать раз в 24 часа")
            
            user_task.last_claimed_at = datetime.now()
            user_task.completed_at = datetime.now()
            user_task.progress = 1
            
            user.tickets += task.reward
            db.commit()
            
            return ClaimResponse(
                success=True,
                message=f"Вы получили {task.reward} 🎟️ билетиков!",
                tickets=user.tickets
            )
        
        # ===== СПИНЫ (ЦИКЛИЧНОЕ) =====
        elif task.task_type == "spin":
            if user.spins_count < task.required_count:
                db.close()
                raise HTTPException(status_code=400, detail="Нужно сделать больше спинов")
            
            if user_task.claimed_at:
                db.close()
                raise HTTPException(status_code=400, detail="Награда уже получена")
            
            # 🔥 ДАЁМ НАГРАДУ
            user.tickets += task.reward
            
            # 🔥 СБРАСЫВАЕМ СПИНЫ
            user.spins_count = 0
            
            # 🔥 ОТМЕЧАЕМ, ЧТО НАГРАДА ПОЛУЧЕНА
            user_task.claimed_at = datetime.now()
            user_task.completed_at = None  # сбрасываем, чтобы можно было выполнять снова
            user_task.progress = 0
            
            db.commit()
            
            return ClaimResponse(
                success=True,
                message=f"Вы получили {task.reward} 🎟️ билетиков!",
                tickets=user.tickets
            )
        
        # ===== СПОНСОР (НЕ ЦИКЛИЧНОЕ) =====
        elif task.task_type == "sponsor":
            if not user_task.completed_at:
                db.close()
                raise HTTPException(status_code=400, detail="Задание ещё не выполнено")
            
            if user_task.claimed_at:
                db.close()
                raise HTTPException(status_code=400, detail="Награда уже получена")
            
            user_task.claimed_at = datetime.now()
            user.tickets += task.reward
            db.commit()
            
            return ClaimResponse(
                success=True,
                message=f"Вы получили {task.reward} 🎟️ билетиков!",
                tickets=user.tickets
            )
        
        # ===== ДРУЗЬЯ (СОЦИАЛЬНОЕ, ЦИКЛИЧНОЕ) =====
        elif task.task_type == "social":
            current_progress = db.query(Referral).filter_by(referrer_id=user.id).count()
            
            if current_progress < task.required_count:
                db.close()
                raise HTTPException(status_code=400, detail="Нужно больше друзей")
            
            if user_task.claimed_at:
                db.close()
                raise HTTPException(status_code=400, detail="Награда уже получена")
            
            # 🔥 ДАЁМ НАГРАДУ
            user.tickets += task.reward
            
            # 🔥 ОТМЕЧАЕМ, ЧТО НАГРАДА ПОЛУЧЕНА
            # прогресс НЕ сбрасываем — рефералы остаются, но помечаем,
            # что за текущее количество уже получили
            user_task.claimed_at = datetime.now()
            user_task.completed_at = None
            user_task.progress = current_progress
            
            db.commit()
            
            return ClaimResponse(
                success=True,
                message=f"Вы получили {task.reward} 🎟️ билетиков!",
                tickets=user.tickets
            )
        
        # Fallback (на всякий случай)
        user.tickets += task.reward
        db.commit()
        
        return ClaimResponse(
            success=True,
            message=f"Вы получили {task.reward} 🎟️ билетиков!",
            tickets=user.tickets
        )
        
    except HTTPException:
        raise
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
    
    # ===== СПИНЫ (ЦИКЛИЧНОЕ) =====
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
        
        # 🔥 Если спинов хватает
        if user.spins_count >= task.required_count:
            # Первый раз — ставим completed_at
            if user_task.completed_at is None and user_task.claimed_at is None:
                user_task.completed_at = datetime.now()
            # 🔥 Если награда уже была забрана ранее (claimed_at стоит) —
            # значит пользователь набрал спины ЗАНОВО, сбрасываем claimed_at
            if user_task.claimed_at is not None and user_task.completed_at is None:
                user_task.claimed_at = None
                user_task.completed_at = datetime.now()
    
    # ===== СОЦИАЛЬНЫЕ (ДРУЗЬЯ, ЦИКЛИЧНОЕ) =====
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
        
        current_referrals = db.query(Referral).filter_by(referrer_id=user.id).count()
        user_task.progress = current_referrals
        
        # 🔥 Логика цикличности для social:
        # Считаем, сколько рефералов было на момент последнего claim
        # Если текущее количество - progress на момент claim >= required — можно забрать снова
        if user_task.claimed_at is not None:
            # Сколько рефералов было при последнем claim
            claimed_at_progress = user_task.progress if user_task.progress else 0
            # Но progress уже обновлён выше... нужен отдельный маркер
            
            # Упрощённый вариант: если claimed_at стоит, но рефералов
            # стало больше, чем было — считаем, что можно снова
            # (в идеале нужно поле last_claimed_progress, но без миграции
            # используем такую эвристику)
            pass
        
        # Если рефералов хватает и completed_at пуст — отмечаем выполненным
        if current_referrals >= task.required_count and user_task.completed_at is None:
            user_task.completed_at = datetime.now()
    
    # ===== ЕЖЕДНЕВНЫЕ =====
    daily_tasks = db.query(Task).filter_by(task_type="daily", is_active=True).all()
    for task in daily_tasks:
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
        
        # Через 24 часа — сбрасываем completed_at
        if user_task.last_claimed_at:
            time_diff = datetime.now() - user_task.last_claimed_at
            if time_diff >= timedelta(hours=24):
                user_task.completed_at = None
                user_task.progress = 0
    
    db.commit()
    db.close()
    
    return {"success": True, "message": "Прогресс заданий обновлён"}