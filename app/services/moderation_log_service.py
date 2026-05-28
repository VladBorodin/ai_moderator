from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.moderation_log import ModerationLog


class ModerationLogService:
	def __init__(self, db: Session) -> None:
		self.db = db

	def create_log(
		self,
		request_json: dict,
		chat_id: str | None = None,
		user_id: str | None = None,
		trigger_word: str | None = None
	) -> ModerationLog:
		moderation_log = ModerationLog(
			chat_id=chat_id,
			user_id=user_id,
			trigger_word=trigger_word,
			request_json=request_json
		)

		self.db.add(moderation_log)
		self.db.commit()
		self.db.refresh(moderation_log)

		return moderation_log

	def complete_log(
		self,
		moderation_log_id: int,
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
		moderation_log_id: int,
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