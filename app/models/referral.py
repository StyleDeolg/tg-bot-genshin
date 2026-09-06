import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    referred_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    reward_claimed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    referrer = relationship("User", foreign_keys=[referrer_id], backref="referrals_given")
    referred = relationship("User", foreign_keys=[referred_id], backref="referrals_received")

    def __repr__(self):
        return f"<Referral {self.referrer_id} -> {self.referred_id}>"


class ReferralReward(Base):
    __tablename__ = "referral_rewards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level = Column(Integer, nullable=False, unique=True)
    reward = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())