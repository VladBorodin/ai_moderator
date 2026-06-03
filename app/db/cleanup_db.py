import logging

from sqlalchemy.orm import Session

from app.services.moderation_log_service import ModerationLogService
from app.services.system_setting_service import SystemSettingService


logger = logging.getLogger(__name__)


def cleanup_db(db: Session) -> None:
	cleanup_moderation_logs(db)


def cleanup_moderation_logs(db: Session) -> None:
	system_setting_service = SystemSettingService(db)

	retention_days = system_setting_service.get_int(
		code="moderation.log_retention_days",
		default_value=120
	)

	if retention_days <= 0:
		logger.info(
			"Moderation log cleanup skipped. retention_days=%s",
			retention_days
		)

		return

	moderation_log_service = ModerationLogService(db)

	deleted_count = moderation_log_service.delete_older_than_days(
		days=retention_days
	)

	logger.info(
		"Moderation log cleanup completed. retention_days=%s deleted_count=%s",
		retention_days,
		deleted_count
	)