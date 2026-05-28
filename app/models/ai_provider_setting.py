from datetime import datetime

from app.util.date_time import get_utc_now

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AiProviderSetting(Base):
	__tablename__ = "ai_provider_setting"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	name: Mapped[str] = mapped_column(String(100), nullable=False)
	provider_type: Mapped[str] = mapped_column(String(50), nullable=False)
	provider_url: Mapped[str] = mapped_column(Text, nullable=False)
	model_name: Mapped[str] = mapped_column(String(200), nullable=False)
	api_key: Mapped[str | None] = mapped_column(Text, nullable=True)
	timeout_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
	is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
	created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)
	modified_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)