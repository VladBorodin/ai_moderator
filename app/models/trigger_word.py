from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.util.date_time import get_utc_now


class TriggerWord(Base):
	__tablename__ = "trigger_word"

	id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
	word: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
	language: Mapped[str | None] = mapped_column(String(20), nullable=True)
	comment: Mapped[str | None] = mapped_column(Text, nullable=True)
	is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
	created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)
	modified_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)