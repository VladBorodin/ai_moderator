from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SystemSettingUpdateDto(BaseModel):
	value: str | None = None
	description: str | None = None


class SystemSettingDto(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	code: str
	value: str | None = None
	description: str | None = None
	created_on: datetime
	modified_on: datetime