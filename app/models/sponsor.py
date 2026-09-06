import uuid
from sqlalchemy import Column, String, Integer, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    logo_url = Column(String, nullable=True)
    link = Column(String, nullable=True)
    channel = Column(String, nullable=True)  # @username канала для подписки
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Sponsor {self.name}>"