from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ai_provider_setting import (
	AiProviderSettingCreateDto,
	AiProviderSettingDto,
	AiProviderSettingUpdateDto
)
from app.services.ai_provider_setting_service import AiProviderSettingService


router = APIRouter(
	prefix="/settings/ai-providers",
	tags=["AI Provider Settings"]
)


@router.get("", response_model=list[AiProviderSettingDto])
def get_ai_providers(
	db: Session = Depends(get_db)
) -> list[AiProviderSettingDto]:
	service = AiProviderSettingService(db)
	return service.get_all()


@router.get("/active", response_model=AiProviderSettingDto | None)
def get_active_ai_provider(
	db: Session = Depends(get_db)
) -> AiProviderSettingDto | None:
	service = AiProviderSettingService(db)
	return service.get_active()


@router.post("", response_model=AiProviderSettingDto)
def create_ai_provider(
	dto: AiProviderSettingCreateDto,
	db: Session = Depends(get_db)
) -> AiProviderSettingDto:
	service = AiProviderSettingService(db)
	return service.create(dto)


@router.put("/{provider_id}", response_model=AiProviderSettingDto)
def update_ai_provider(
	provider_id: UUID,
	dto: AiProviderSettingUpdateDto,
	db: Session = Depends(get_db)
) -> AiProviderSettingDto:
	service = AiProviderSettingService(db)

	provider = service.update(
		provider_id=provider_id,
		dto=dto
	)

	if provider is None:
		raise HTTPException(
			status_code=404,
			detail="AI provider setting was not found."
		)

	return provider


@router.post("/{provider_id}/activate", response_model=AiProviderSettingDto)
def activate_ai_provider(
	provider_id: UUID,
	db: Session = Depends(get_db)
) -> AiProviderSettingDto:
	service = AiProviderSettingService(db)

	provider = service.activate(provider_id)

	if provider is None:
		raise HTTPException(
			status_code=404,
			detail="AI provider setting was not found."
		)

	return provider