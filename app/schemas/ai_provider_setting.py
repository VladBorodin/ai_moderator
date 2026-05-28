from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AiProviderSettingCreateDto(BaseModel):
	name: str = Field(min_length=1, max_length=100)
	provider_type: str = Field(default="openai_compatible", min_length=1, max_length=50)
	provider_url: str = Field(min_length=1)
	model_name: str = Field(min_length=1, max_length=200)
	api_key: str | None = None
	timeout_seconds: int = Field(default=60, ge=1, le=600)
	is_active: bool = False


class AiProviderSettingUpdateDto(BaseModel):
	name: str = Field(min_length=1, max_length=100)
	provider_type: str = Field(min_length=1, max_length=50)
	provider_url: str = Field(min_length=1)
	model_name: str = Field(min_length=1, max_length=200)
	api_key: str | None = None
	timeout_seconds: int = Field(ge=1, le=600)
	is_active: bool = False


class AiProviderSettingDto(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	name: str
	provider_type: str
	provider_url: str
	model_name: str
	api_key: str | None = None
	timeout_seconds: int
	is_active: bool
	created_on: datetime
	modified_on: datetime