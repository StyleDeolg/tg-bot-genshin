import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ===== БОТ =====
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "GenshinPool")  # 🔥 ИСПРАВЛЕНО
    BOT_MODE: str = os.getenv("BOT_MODE", "webhook")
    
    # ===== API =====
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    PORT: int = int(os.getenv("PORT", 8000))
    
    # ===== БАЗА ДАННЫХ =====
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # ===== WEBHOOK =====
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_SECRET_TOKEN: str = os.getenv("WEBHOOK_SECRET_TOKEN", "")
    
    # ===== АДМИНЫ =====
    @property
    def ADMIN_IDS(self) -> list[int]:
        """Список Telegram ID администраторов"""
        admin_str = os.getenv("ADMIN_IDS", "")
        if not admin_str:
            return []
        return [int(id.strip()) for id in admin_str.split(",") if id.strip()]
    
    # ===== ДОНАТОРЫ =====
    @property
    def DONATOR_CHAT_IDS(self) -> list[int]:
        """Список Telegram ID донаторов для уведомлений"""
        donator_str = os.getenv("DONATOR_CHAT_IDS", "")
        if not donator_str:
            return []
        return [int(id.strip()) for id in donator_str.split(",") if id.strip()]
    
    # ===== ОПЦИОНАЛЬНО =====
    @property
    def DONATOR_ID(self) -> int | None:
        """Один донатор (устаревшее, используй DONATOR_CHAT_IDS)"""
        donator = os.getenv("DONATOR_ID", "")
        return int(donator) if donator else None

config = Config()