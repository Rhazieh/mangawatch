from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.database import Base


class Series(Base):
    __tablename__ = "series"

    id = Column(Integer, primary_key=True, index=True)
    source_url = Column(String, unique=True, nullable=False, index=True)
    source_type = Column(String, nullable=False)
    external_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    series_id = Column(Integer, ForeignKey("series.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("user_id", "series_id", name="uq_user_series"),)
