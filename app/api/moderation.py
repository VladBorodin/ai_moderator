from typing import Any

from fastapi import APIRouter

from app.core.config import settings
from app.services.ai_moderation_service import AiModerationService


router = APIRouter(
	prefix="/moderation",
	tags=["Moderation"]
)


@router.post("/check")
def check_message(request_data: dict[str, Any]) -> dict[str, Any]:
	moderation_service = AiModerationService(
		provider_url=settings.ai_provider_url,
		model_name=settings.ai_model_name,
		api_key=settings.ai_api_key,
		timeout_seconds=settings.ai_timeout_seconds
	)

	result = moderation_service.moderate(request_data)

	return {
		"chat_id": request_data.get("chat_id"),
		"user_id": request_data.get("user_id"),
		"result": result
	}