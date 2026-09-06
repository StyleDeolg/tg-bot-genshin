import uuid
from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class WheelSpin(Base):
    __tablename__ = "wheel_spins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    prize = Column(String, nullable=False)
    prize_value = Column(Integer, nullable=False)
    prize_type = Column(String, nullable=True)  # moon, shard, crystals_60, crystals_330, empty
    created_at = Column(DateTime, server_default=func.now())


class WheelConfig(Base):
    __tablename__ = "wheel_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    value = Column(Integer, nullable=False)
    chance = Column(Integer, nullable=False)
    emoji = Column(String, nullable=True)
    is_active = Column(String, default="true")
    prize_type = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())