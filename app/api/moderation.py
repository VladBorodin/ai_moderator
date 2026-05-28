import logging

from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.moderation import (
	ModerationCheckRequestDto,
	ModerationCheckResponseDto,
	ModerationLogDto,
	ModerationResultDto
)
from app.services.moderation_log_service import ModerationLogService


logger = logging.getLogger(__name__)

router = APIRouter(
	prefix="/moderation",
	tags=["Moderation"]
)


@router.post("/check", response_model=ModerationCheckResponseDto)
def check_message(
	request_data: ModerationCheckRequestDto,
	db: Session = Depends(get_db)
) -> ModerationCheckResponseDto:
	moderation_log_service = ModerationLogService(db)

	request_json = request_data.model_dump(mode="json")

	last_message_text = _get_last_message_text(request_data)
	last_message_name = _get_last_message_name(request_data)
	user_name = request_data.user_name or last_message_name

	moderation_log = moderation_log_service.create_log(
		source_system=request_data.source_system,
		chat_id=request_data.chat_id,
		user_id=request_data.user_id,
		user_name=user_name,
		external_message_id=request_data.external_message_id,
		last_message_text=last_message_text,
		request_json=request_json
	)

	start_time = perf_counter()

	try:
		result = _create_mock_moderation_result()

		processing_time_ms = int((perf_counter() - start_time) * 1000)

		moderation_log_service.complete_log(
			moderation_log_id=moderation_log.id,
			response_json=result.model_dump(mode="json"),
			verdict=result.verdict,
			offense_level=result.offense_level,
			description=result.description,
			processing_time_ms=processing_time_ms
		)

		return ModerationCheckResponseDto(
			chat_id=request_data.chat_id,
			user_id=request_data.user_id,
			result=result
		)

	except Exception as error:
		processing_time_ms = int((perf_counter() - start_time) * 1000)

		moderation_log_service.fail_log(
			moderation_log_id=moderation_log.id,
			error_text=str(error),
			processing_time_ms=processing_time_ms
		)

		logger.exception("Moderation check failed. moderation_log_id=%s", moderation_log.id)

		raise HTTPException(
			status_code=500,
			detail="Moderation check failed."
		) from error


@router.get("/logs", response_model=list[ModerationLogDto])
def get_moderation_logs(
	limit: int = Query(default=50, ge=1, le=200),
	offset: int = Query(default=0, ge=0),
	db: Session = Depends(get_db)
) -> list[ModerationLogDto]:
	moderation_log_service = ModerationLogService(db)

	return moderation_log_service.get_logs(
		limit=limit,
		offset=offset
	)


def _create_mock_moderation_result() -> ModerationResultDto:
	return ModerationResultDto(
		verdict=0,
		offense_level=0,
		description="Mock moderation result. AI provider is not connected yet."
	)

def _get_last_message_text(request_data: ModerationCheckRequestDto) -> str | None:
	if not request_data.messages:
		return None

	return request_data.messages[-1].text

def _get_last_message_name(request_data: ModerationCheckRequestDto) -> str | None:
	if not request_data.messages:
		return None

	return request_data.messages[-1].name