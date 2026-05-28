from typing import Any

from pydantic import BaseModel, Field


class ChatMessageDto(BaseModel):
	role: str = Field(default="user")
	name: str | None = None
	text: str


class ModerationCheckRequestDto(BaseModel):
	chat_id: str | None = None
	user_id: str | None = None
	trigger_word: str | None = None
	messages: list[ChatMessageDto]


class ModerationResultDto(BaseModel):
	verdict: int = Field(ge=0, le=1)
	offense_level: int = Field(ge=0, le=10)
	description: str


class ModerationCheckResponseDto(BaseModel):
	chat_id: str | None = None
	user_id: str | None = None
	result: ModerationResultDto


class ModerationLogDto(BaseModel):
	id: int
	chat_id: str | None = None
	user_id: str | None = None
	trigger_word: str | None = None
	request_json: dict[str, Any]
	response_json: dict[str, Any] | None = None
	verdict: int | None = None
	offense_level: int | None = None
	description: str | None = None
	error_text: str | None = None

	class Config:
		from_attributes = True