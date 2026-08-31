from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, LargeBinary, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class CalendarCredential(Base):
    __tablename__ = "calendar_credentials"
    __table_args__ = (UniqueConstraint("user_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    encrypted_token: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    scopes: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str] = mapped_column(String(30), default="google")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="calendar_credential")
