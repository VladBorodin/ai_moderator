from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.prompt_template import PromptTemplate
from app.schemas.prompt_template import (
	PromptTemplateCreateDto,
	PromptTemplateUpdateDto
)


class PromptTemplateService:
	def __init__(self, db: Session) -> None:
		self.db = db

	def get_all(self) -> list[PromptTemplate]:
		statement = (
			select(PromptTemplate)
			.where(PromptTemplate.is_deleted.is_(False))
			.order_by(PromptTemplate.created_on.desc())
		)

		return list(self.db.scalars(statement).all())

	def get_by_id(self, prompt_template_id: UUID) -> PromptTemplate | None:
		return self.db.get(PromptTemplate, prompt_template_id)

	def get_active(self) -> PromptTemplate | None:
		statement = (
			select(PromptTemplate)
			.where(PromptTemplate.is_active.is_(True))
			.where(PromptTemplate.is_deleted.is_(False))
			.order_by(PromptTemplate.modified_on.desc())
			.limit(1)
		)

		return self.db.scalars(statement).first()

	def create(self, dto: PromptTemplateCreateDto) -> PromptTemplate:
		if dto.is_active:
			self._deactivate_all()

		prompt_template = PromptTemplate(
			code=dto.code,
			name=dto.name,
			prompt_text=dto.prompt_text,
			version=dto.version,
			is_active=dto.is_active
		)

		self.db.add(prompt_template)
		self.db.commit()
		self.db.refresh(prompt_template)

		return prompt_template

	def update(
		self,
		prompt_template_id: UUID,
		dto: PromptTemplateUpdateDto
	) -> PromptTemplate | None:
		prompt_template = self.get_by_id(prompt_template_id)

		if prompt_template is None:
			return None

		if prompt_template.is_deleted:
			return None

		if dto.is_active:
			self._deactivate_all(exclude_prompt_template_id=prompt_template_id)

		prompt_template.code = dto.code
		prompt_template.name = dto.name
		prompt_template.prompt_text = dto.prompt_text
		prompt_template.version = dto.version
		prompt_template.is_active = dto.is_active

		self.db.commit()
		self.db.refresh(prompt_template)

		return prompt_template

	def activate(self, prompt_template_id: UUID) -> PromptTemplate | None:
		prompt_template = self.get_by_id(prompt_template_id)

		if prompt_template is None:
			return None

		if prompt_template.is_deleted:
			return None

		self._deactivate_all(exclude_prompt_template_id=prompt_template_id)

		prompt_template.is_active = True

		self.db.commit()
		self.db.refresh(prompt_template)

		return prompt_template

	def delete(self, prompt_template_id: UUID) -> bool:
		prompt_template = self.get_by_id(prompt_template_id)

		if prompt_template is None:
			return False

		if prompt_template.is_deleted:
			return False

		if prompt_template.is_active:
			raise ValueError("Active prompt template cannot be deleted.")

		prompt_template.is_deleted = True
		prompt_template.is_active = False

		self.db.commit()

		return True

	def _deactivate_all(
		self,
		exclude_prompt_template_id: UUID | None = None
	) -> None:
		statement = (
			select(PromptTemplate)
			.where(PromptTemplate.is_deleted.is_(False))
		)

		if exclude_prompt_template_id is not None:
			statement = statement.where(PromptTemplate.id != exclude_prompt_template_id)

		prompt_templates = list(self.db.scalars(statement).all())

		for prompt_template in prompt_templates:
			prompt_template.is_active = False