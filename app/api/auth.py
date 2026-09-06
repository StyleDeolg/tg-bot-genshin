from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import uuid
from app.database import SessionLocal
from app.models.user import User
from app.config import config

router = APIRouter(prefix="/api/auth", tags=["auth"])

class AuthRequest(BaseModel):
    telegram_id: str
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None

class AuthResponse(BaseModel):
    public_id: str
    telegram_id: str
    username: str | None
    first_name: str | None
    last_name: str | None
    genshin_uid: str | None
    genshin_server: str | None

@router.post("/login", response_model=AuthResponse)
async def login(request: AuthRequest):
    db = SessionLocal()
    
    user = db.query(User).filter_by(telegram_id=request.telegram_id).first()
    
    if not user:
        new_user = User(
            telegram_id=request.telegram_id,
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            public_id=uuid.uuid4(),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user
    
    db.close()
    
    return AuthResponse(
        public_id=str(user.public_id),
        telegram_id=str(user.telegram_id),
        username=str(user.username) if user.username else None,
        first_name=str(user.first_name) if user.first_name else None,
        last_name=str(user.last_name) if user.last_name else None,
        genshin_uid=user.genshin_uid,
        genshin_server=user.genshin_server,
    )


@router.get("/avatar/{telegram_id}")
async def get_avatar(telegram_id: str):
    """Получает ссылку на аватарку пользователя из Telegram"""
    try:
        db = SessionLocal()
        user = db.query(User).filter_by(telegram_id=telegram_id).first()
        db.close()
        
        if not user:
            return {"avatar_url": None, "error": "Пользователь не найден"}
        
        url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getUserProfilePhotos"
        params = {"user_id": int(telegram_id), "limit": 1}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            data = response.json()
            
            if not data.get("ok"):
                print(f"Telegram API error: {data}")
                return {"avatar_url": None}
            
            photos = data.get("result", {}).get("photos", [])
            if not photos:
                return {"avatar_url": None}
            
            file_id = photos[0][0]["file_id"]
            
            file_url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getFile"
            file_response = await client.get(file_url, params={"file_id": file_id})
            file_data = file_response.json()
            
            if not file_data.get("ok"):
                print(f"Telegram API file error: {file_data}")
                return {"avatar_url": None}
            
            file_path = file_data["result"]["file_path"]
            avatar_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file_path}"
            
            return {"avatar_url": avatar_url}
            
    except httpx.TimeoutException:
        print("Timeout при запросе к Telegram API")
        return {"avatar_url": None}
    except Exception as e:
        print(f"Ошибка получения аватарки: {e}")
        return {"avatar_url": None}