from datetime import datetime

from app.util.date_time import get_utc_now

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class PromptTemplate(Base):
	__tablename__ = "prompt_template"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
	name: Mapped[str] = mapped_column(String(200), nullable=False)
	prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
	version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
	is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
	created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)
	modified_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)