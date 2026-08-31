from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class PendingAction(Base):
    __tablename__ = "pending_actions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"), index=True)
    thread_id: Mapped[str] = mapped_column(String(100), index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user = relationship("User")
    trip = relationship("Trip")
