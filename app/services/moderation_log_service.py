from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.moderation_log import ModerationLog


class ModerationLogService:
	def __init__(self, db: Session) -> None:
		self.db = db

	def create_log(
		self,
		request_json: dict,
		source_system: str | None = None,
		chat_id: str | None = None,
		user_id: str | None = None,
		user_name: str | None = None,
		external_message_id: str | None = None,
		last_message_text: str | None = None
	) -> ModerationLog:
		moderation_log = ModerationLog(
			source_system=source_system,
			chat_id=chat_id,
			user_id=user_id,
			user_name=user_name,
			external_message_id=external_message_id,
			last_message_text=last_message_text,
			request_json=request_json
		)

		self.db.add(moderation_log)
		self.db.commit()
		self.db.refresh(moderation_log)

		return moderation_log

	def complete_log(
		self,
		moderation_log_id: UUID,
		response_json: dict,
		verdict: int,
		offense_level: int,
		description: str,
		processing_time_ms: int
	) -> ModerationLog:
		moderation_log = self.db.get(ModerationLog, moderation_log_id)

		if moderation_log is None:
			raise ValueError(f"Moderation log with id {moderation_log_id} was not found.")

		moderation_log.response_json = response_json
		moderation_log.verdict = verdict
		moderation_log.offense_level = offense_level
		moderation_log.description = description
		moderation_log.processing_time_ms = processing_time_ms
		moderation_log.error_text = None

		self.db.commit()
		self.db.refresh(moderation_log)

		return moderation_log

	def fail_log(
		self,
		moderation_log_id: UUID,
		error_text: str,
		processing_time_ms: int | None = None
	) -> ModerationLog:
		moderation_log = self.db.get(ModerationLog, moderation_log_id)

		if moderation_log is None:
			raise ValueError(f"Moderation log with id {moderation_log_id} was not found.")

		moderation_log.error_text = error_text
		moderation_log.processing_time_ms = processing_time_ms

		self.db.commit()
		self.db.refresh(moderation_log)

		return moderation_log

	def get_logs(
		self,
		limit: int = 50,
		offset: int = 0
	) -> list[ModerationLog]:
		statement = (
			select(ModerationLog)
			.order_by(ModerationLog.created_on.desc())
			.offset(offset)
			.limit(limit)
		)

		return list(self.db.scalars(statement).all())