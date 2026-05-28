from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_provider_setting import AiProviderSetting
from app.schemas.ai_provider_setting import (
	AiProviderSettingCreateDto,
	AiProviderSettingUpdateDto
)


class AiProviderSettingService:
	def __init__(self, db: Session) -> None:
		self.db = db

	def get_all(self) -> list[AiProviderSetting]:
		statement = (
			select(AiProviderSetting)
			.order_by(AiProviderSetting.created_on.desc())
		)

		return list(self.db.scalars(statement).all())

	def get_by_id(self, provider_id: UUID) -> AiProviderSetting | None:
		return self.db.get(AiProviderSetting, provider_id)

	def get_active(self) -> AiProviderSetting | None:
		statement = (
			select(AiProviderSetting)
			.where(AiProviderSetting.is_active.is_(True))
			.order_by(AiProviderSetting.modified_on.desc())
			.limit(1)
		)

		return self.db.scalars(statement).first()

	def create(self, dto: AiProviderSettingCreateDto) -> AiProviderSetting:
		if dto.is_active:
			self._deactivate_all()

		provider = AiProviderSetting(
			name=dto.name,
			provider_type=dto.provider_type,
			provider_url=dto.provider_url,
			model_name=dto.model_name,
			api_key=dto.api_key,
			timeout_seconds=dto.timeout_seconds,
			is_active=dto.is_active
		)

		self.db.add(provider)
		self.db.commit()
		self.db.refresh(provider)

		return provider

	def update(
		self,
		provider_id: UUID,
		dto: AiProviderSettingUpdateDto
	) -> AiProviderSetting | None:
		provider = self.get_by_id(provider_id)

		if provider is None:
			return None

		if dto.is_active:
			self._deactivate_all(exclude_provider_id=provider_id)

		provider.name = dto.name
		provider.provider_type = dto.provider_type
		provider.provider_url = dto.provider_url
		provider.model_name = dto.model_name
		provider.api_key = dto.api_key
		provider.timeout_seconds = dto.timeout_seconds
		provider.is_active = dto.is_active

		self.db.commit()
		self.db.refresh(provider)

		return provider

	def activate(self, provider_id: UUID) -> AiProviderSetting | None:
		provider = self.get_by_id(provider_id)

		if provider is None:
			return None

		self._deactivate_all(exclude_provider_id=provider_id)

		provider.is_active = True

		self.db.commit()
		self.db.refresh(provider)

		return provider

	def _deactivate_all(
		self,
		exclude_provider_id: UUID | None = None
	) -> None:
		statement = select(AiProviderSetting)

		if exclude_provider_id is not None:
			statement = statement.where(AiProviderSetting.id != exclude_provider_id)

		providers = list(self.db.scalars(statement).all())

		for provider in providers:
			provider.is_active = False