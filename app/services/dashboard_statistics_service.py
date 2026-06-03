from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.moderation_log import ModerationLog
from app.services.ai_provider_setting_service import AiProviderSettingService
from app.services.prompt_template_service import PromptTemplateService


class DashboardStatisticsService:
	def __init__(self, db: Session) -> None:
		self.db = db

	def get_statistics(self, days: int = 14) -> dict[str, Any]:
		summary = self._get_summary()
		active_provider = self._get_active_provider_info()
		active_prompt = self._get_active_prompt_info()

		recent_error_summary = self._get_recent_error_summary(hours=24)

		return {
			"summary": summary,
			"recent_error_summary": recent_error_summary,
			"active_provider": active_provider,
			"active_prompt": active_prompt,
			"warnings": self._get_warnings(
				summary=summary,
				recent_error_summary=recent_error_summary,
				active_provider=active_provider,
				active_prompt=active_prompt
			),
			"verdict_distribution": self._get_verdict_distribution(summary),
			"offense_level_distribution": self._get_offense_level_distribution(),
			"checks_by_day": self._get_checks_by_day(days)
		}

	def _get_summary(self) -> dict[str, int | float | None]:
		statement = select(
			func.count(ModerationLog.id).label("total_checks"),
			func.sum(
				case(
					(ModerationLog.verdict == 1, 1),
					else_=0
				)
			).label("offensive_checks"),
			func.sum(
				case(
					(ModerationLog.verdict == 0, 1),
					else_=0
				)
			).label("non_offensive_checks"),
			func.sum(
				case(
					(ModerationLog.error_text.is_not(None), 1),
					else_=0
				)
			).label("failed_checks"),
			func.avg(ModerationLog.processing_time_ms).label("average_processing_time_ms")
		)

		result = self.db.execute(statement).one()

		return {
			"total_checks": int(result.total_checks or 0),
			"offensive_checks": int(result.offensive_checks or 0),
			"non_offensive_checks": int(result.non_offensive_checks or 0),
			"failed_checks": int(result.failed_checks or 0),
			"average_processing_time_ms": round(float(result.average_processing_time_ms), 2)
			if result.average_processing_time_ms is not None
			else None
		}

	def _get_active_provider_info(self) -> dict[str, Any] | None:
		service = AiProviderSettingService(self.db)
		provider = service.get_active()

		if provider is None:
			return None

		return {
			"id": str(provider.id),
			"name": provider.name,
			"provider_type": provider.provider_type,
			"provider_url": provider.provider_url,
			"model_name": provider.model_name,
			"timeout_seconds": provider.timeout_seconds
		}

	def _get_active_prompt_info(self) -> dict[str, Any] | None:
		service = PromptTemplateService(self.db)
		prompt = service.get_active()

		if prompt is None:
			return None

		return {
			"id": str(prompt.id),
			"code": prompt.code,
			"name": prompt.name,
			"version": prompt.version,
			"length": len(prompt.prompt_text)
		}

	def _get_verdict_distribution(
		self,
		summary: dict[str, int | float | None]
	) -> list[dict[str, int | str]]:
		return [
			{
				"name": "no_offensive",
				"value": int(summary["non_offensive_checks"] or 0)
			},
			{
				"name": "offensive",
				"value": int(summary["offensive_checks"] or 0)
			},
			{
				"name": "failed",
				"value": int(summary["failed_checks"] or 0)
			}
		]

	def _get_offense_level_distribution(self) -> list[dict[str, int]]:
		statement = (
			select(
				ModerationLog.offense_level,
				func.count(ModerationLog.id)
			)
			.where(ModerationLog.offense_level.is_not(None))
			.group_by(ModerationLog.offense_level)
			.order_by(ModerationLog.offense_level)
		)

		rows = self.db.execute(statement).all()
		count_by_level = {
			int(row[0]): int(row[1])
			for row in rows
		}

		return [
			{
				"level": level,
				"count": count_by_level.get(level, 0)
			}
			for level in range(0, 11)
		]

	def _get_checks_by_day(self, days: int) -> list[dict[str, int | str]]:
		normalized_days = max(1, min(days, 90))
		today = datetime.now(UTC).date()
		start_date = today - timedelta(days=normalized_days - 1)

		statement = (
			select(
				func.date(ModerationLog.created_on).label("created_date"),
				func.count(ModerationLog.id).label("total"),
				func.sum(
					case(
						(ModerationLog.error_text.is_not(None), 1),
						else_=0
					)
				).label("failed")
			)
			.where(ModerationLog.created_on >= datetime.combine(start_date, datetime.min.time(), tzinfo=UTC))
			.group_by(func.date(ModerationLog.created_on))
			.order_by(func.date(ModerationLog.created_on))
		)

		rows = self.db.execute(statement).all()

		data_by_date = {
			str(row.created_date): {
				"total": int(row.total or 0),
				"failed": int(row.failed or 0)
			}
			for row in rows
		}

		result: list[dict[str, int | str]] = []

		for day_offset in range(normalized_days):
			current_date = start_date + timedelta(days=day_offset)
			date_key = str(current_date)
			day_data = data_by_date.get(
				date_key,
				{
					"total": 0,
					"failed": 0
				}
			)

			result.append(
				{
					"date": date_key,
					"total": day_data["total"],
					"failed": day_data["failed"]
				}
			)

		return result
	
	def _get_warnings(
		self,
		summary: dict[str, int | float | None],
		recent_error_summary: dict[str, int | float],
		active_provider: dict[str, Any] | None,
		active_prompt: dict[str, Any] | None
	) -> list[dict[str, str]]:
		warnings: list[dict[str, str]] = []

		if active_provider is None:
			warnings.append(
				{
					"level": "danger",
					"title": "AI provider не настроен",
					"description": "Активный AI provider отсутствует. Новые проверки не смогут обращаться к ИИ."
				}
			)

		if active_prompt is None:
			warnings.append(
				{
					"level": "danger",
					"title": "Активный промт не настроен",
					"description": "Активный prompt template отсутствует. Новые проверки не смогут сформировать системную инструкцию."
				}
			)

		recent_failed_checks = int(recent_error_summary["failed_checks"] or 0)
		recent_total_checks = int(recent_error_summary["total_checks"] or 0)
		recent_error_rate = float(recent_error_summary["error_rate"] or 0)

		if recent_failed_checks > 0:
			warnings.append(
				{
					"level": "warning",
					"title": "Есть недавние ошибки проверок",
					"description": f"За последние 24 часа найдено ошибок: {recent_failed_checks}. Проверь системные логи и журнал проверок."
				}
			)

		if recent_total_checks >= 10 and recent_error_rate >= 0.2:
			warnings.append(
				{
					"level": "danger",
					"title": "Высокая доля недавних ошибок",
					"description": f"За последние 24 часа доля ошибок составляет {round(recent_error_rate * 100, 1)}%. Возможна проблема с AI provider или настройками."
				}
			)

		if not warnings:
			warnings.append(
				{
					"level": "success",
					"title": "Критичных проблем не обнаружено",
					"description": "Активные настройки найдены. Ошибки можно отслеживать в журнале и системных логах."
				}
			)

		return warnings
	
	def _get_recent_error_summary(self, hours: int = 24) -> dict[str, int | float]:
		start_datetime = datetime.now(UTC) - timedelta(hours=hours)

		statement = select(
			func.count(ModerationLog.id).label("total_checks"),
			func.sum(
				case(
					(ModerationLog.error_text.is_not(None), 1),
					else_=0
				)
			).label("failed_checks")
		).where(ModerationLog.created_on >= start_datetime)

		result = self.db.execute(statement).one()

		total_checks = int(result.total_checks or 0)
		failed_checks = int(result.failed_checks or 0)

		error_rate = failed_checks / total_checks if total_checks > 0 else 0

		return {
			"total_checks": total_checks,
			"failed_checks": failed_checks,
			"error_rate": error_rate
		}