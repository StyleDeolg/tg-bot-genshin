import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Review(Base):
    """Отзывы пользователей"""
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    is_moderated = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="reviews")

    def __repr__(self):
        return f"<Review user={self.user_id} rating={self.rating}>"