from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.util.date_time import get_utc_now


class SystemSetting(Base):
	__tablename__ = "system_setting"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
	value: Mapped[str | None] = mapped_column(Text, nullable=True)
	description: Mapped[str | None] = mapped_column(Text, nullable=True)
	created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)
	modified_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)