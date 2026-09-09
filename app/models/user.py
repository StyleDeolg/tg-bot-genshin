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
    tickets = Column(Integer, default=2)
    primogems = Column(Integer, default=0)
    spins_count = Column(Integer, default=0)  # ← ДЛЯ ЗАДАНИЙ
    
    # Донат-система
    moon_shards = Column(Integer, default=0)
    has_moon = Column(Boolean, default=False)
    crystals_60_claimed = Column(Boolean, default=False)
    crystals_330_claimed = Column(Boolean, default=False)
    crystals_60_boosted = Column(Boolean, default=True)
    is_donator = Column(Boolean, default=False)
    
    genshin_uid = Column(String, nullable=True)
    genshin_server = Column(String, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.telegram_id}>"