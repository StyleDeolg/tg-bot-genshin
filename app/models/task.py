import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    reward = Column(Integer, nullable=False)  # билетики
    task_type = Column(String, nullable=False)  # social, daily, sponsor
    required_count = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    is_repeatable = Column(Boolean, default=True)  # для daily и social
    sponsor_id = Column(UUID(as_uuid=True), ForeignKey("sponsors.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    sponsor = relationship("Sponsor", backref="tasks")


class UserTask(Base):
    __tablename__ = "user_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    progress = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    last_claimed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="user_tasks")
    task = relationship("Task", backref="user_tasks")