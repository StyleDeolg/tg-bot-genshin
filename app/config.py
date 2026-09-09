import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    BOT_MODE: str = os.getenv("BOT_MODE", "webhook")
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_SECRET_TOKEN: str = os.getenv("WEBHOOK_SECRET_TOKEN", "")
    PORT: int = int(os.getenv("PORT", 8000))
    
    @property
    def ADMIN_IDS(self) -> list[int]:
        """Парсит список админов из .env"""
        admin_str = os.getenv("ADMIN_IDS", "")
        if not admin_str:
            return []
        return [int(id.strip()) for id in admin_str.split(",") if id.strip()]
    
    @property
    def DONATOR_ID(self) -> int:
        """Парсит донатора (если есть)"""
        donator = os.getenv("DONATOR_ID", "")
        return int(donator) if donator else None

config = Config()