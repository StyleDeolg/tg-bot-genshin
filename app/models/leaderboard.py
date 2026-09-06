import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class LeaderboardEntry(Base):
    """Записи в лидерборде"""
    __tablename__ = "leaderboard_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    score_type = Column(String, nullable=False)  # spins, referrals, wins
    score_value = Column(Integer, default=0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="leaderboard_entries")

    def __repr__(self):
        return f"<LeaderboardEntry {self.user_id} {self.score_type}: {self.score_value}>"