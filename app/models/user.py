import uuid
from sqlalchemy import Column, String, DateTime, Integer, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    public_id = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    tickets = Column(Integer, default=10)
    primogems = Column(Integer, default=0)
    
    # --- НОВЫЕ ПОЛЯ ДЛЯ ДОНАТ-СИСТЕМЫ ---
    moon_shards = Column(Integer, default=0)              # осколки луны (0-5)
    has_moon = Column(Boolean, default=False)             # есть ли полная луна
    crystals_60_claimed = Column(Boolean, default=False)  # получал ли 60 кристаллов
    crystals_330_claimed = Column(Boolean, default=False) # получал ли 330 кристаллов
    crystals_60_boosted = Column(Boolean, default=True)   # флаг для 20% шанса (первый раз)
    is_donator = Column(Boolean, default=False)           # роль донатчика
    
    genshin_uid = Column(String, nullable=True)           # Genshin UID
    genshin_server = Column(String, nullable=True)        # asia, eu, us
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.telegram_id}>"