from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PromptTemplateCreateDto(BaseModel):
	code: str = Field(min_length=1, max_length=100)
	name: str = Field(min_length=1, max_length=200)
	prompt_text: str = Field(min_length=1)
	version: int = Field(default=1, ge=1)
	is_active: bool = False


class PromptTemplateUpdateDto(BaseModel):
	code: str = Field(min_length=1, max_length=100)
	name: str = Field(min_length=1, max_length=200)
	prompt_text: str = Field(min_length=1)
	version: int = Field(ge=1)
	is_active: bool = False


class PromptTemplateDto(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	code: str
	name: str
	prompt_text: str
	version: int
	is_active: bool
	is_deleted: bool
	created_on: datetime
	modified_on: datetime