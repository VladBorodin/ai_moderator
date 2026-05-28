from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.prompt_template import (
	PromptTemplateCreateDto,
	PromptTemplateDto,
	PromptTemplateUpdateDto
)
from app.services.prompt_template_service import PromptTemplateService


router = APIRouter(
	prefix="/settings/prompt-templates",
	tags=["Prompt Templates"]
)


@router.get("", response_model=list[PromptTemplateDto])
def get_prompt_templates(
	db: Session = Depends(get_db)
) -> list[PromptTemplateDto]:
	service = PromptTemplateService(db)
	return service.get_all()


@router.get("/active", response_model=PromptTemplateDto | None)
def get_active_prompt_template(
	db: Session = Depends(get_db)
) -> PromptTemplateDto | None:
	service = PromptTemplateService(db)
	return service.get_active()


@router.post("", response_model=PromptTemplateDto)
def create_prompt_template(
	dto: PromptTemplateCreateDto,
	db: Session = Depends(get_db)
) -> PromptTemplateDto:
	service = PromptTemplateService(db)

	try:
		return service.create(dto)
	except ValueError as error:
		raise HTTPException(
			status_code=409,
			detail=str(error)
		) from error


@router.put("/{prompt_template_id}", response_model=PromptTemplateDto)
def update_prompt_template(
	prompt_template_id: UUID,
	dto: PromptTemplateUpdateDto,
	db: Session = Depends(get_db)
) -> PromptTemplateDto:
	service = PromptTemplateService(db)

	try:
		prompt_template = service.update(
			prompt_template_id=prompt_template_id,
			dto=dto
		)
	except ValueError as error:
		raise HTTPException(
			status_code=409,
			detail=str(error)
		) from error

	if prompt_template is None:
		raise HTTPException(
			status_code=404,
			detail="Prompt template was not found."
		)

	return prompt_template


@router.post("/{prompt_template_id}/activate", response_model=PromptTemplateDto)
def activate_prompt_template(
	prompt_template_id: UUID,
	db: Session = Depends(get_db)
) -> PromptTemplateDto:
	service = PromptTemplateService(db)

	prompt_template = service.activate(prompt_template_id)

	if prompt_template is None:
		raise HTTPException(
			status_code=404,
			detail="Prompt template was not found."
		)

	return prompt_template


@router.delete("/{prompt_template_id}")
def delete_prompt_template(
	prompt_template_id: UUID,
	db: Session = Depends(get_db)
) -> dict[str, bool]:
	service = PromptTemplateService(db)

	try:
		is_deleted = service.delete(prompt_template_id)
	except ValueError as error:
		raise HTTPException(
			status_code=400,
			detail=str(error)
		) from error

	if not is_deleted:
		raise HTTPException(
			status_code=404,
			detail="Prompt template was not found."
		)

	return {
		"deleted": True
	}