from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.util.date_time import get_utc_now


class ModerationLog(Base):
	__tablename__ = "moderation_log"

	id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)

	chat_id: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
	user_id: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)

	trigger_word: Mapped[str | None] = mapped_column(String(200), nullable=True)

	request_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
	response_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

	verdict: Mapped[int | None] = mapped_column(Integer, nullable=True)
	offense_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
	description: Mapped[str | None] = mapped_column(Text, nullable=True)

	processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
	error_text: Mapped[str | None] = mapped_column(Text, nullable=True)

	created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)