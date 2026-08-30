from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, ForeignKey, JSON, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Trip(Base):
    __tablename__ = "trips"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    destination: Mapped[str] = mapped_column(String(120))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    budget: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[str] = mapped_column(String(30), default="draft")
    request_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    itinerary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="trips")

