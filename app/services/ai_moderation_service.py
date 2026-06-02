import json
import logging
import re

import requests
from pydantic import ValidationError

from app.models.ai_provider_setting import AiProviderSetting
from app.models.prompt_template import PromptTemplate
from app.schemas.moderation import ModerationCheckRequestDto, ModerationResultDto


logger = logging.getLogger(__name__)


class AiModerationError(Exception):
	pass


class AiProviderRequestError(AiModerationError):
	pass


class AiResponseParseError(AiModerationError):
	pass


class AiResponseValidationError(AiModerationError):
	pass


class AiModerationService:
	def moderate(
		self,
		request_data: ModerationCheckRequestDto,
		provider: AiProviderSetting,
		prompt_template: PromptTemplate
	) -> ModerationResultDto:
		user_prompt = self._build_user_prompt(request_data)

		payload = {
			"model": provider.model_name,
			"messages": [
				{
					"role": "system",
					"content": prompt_template.prompt_text
				},
				{
					"role": "user",
					"content": user_prompt
				}
			],
			"temperature": 0.1
		}

		headers = {
			"Content-Type": "application/json"
		}

		if provider.api_key:
			headers["Authorization"] = f"Bearer {provider.api_key}"

		try:
			response = requests.post(
				provider.provider_url,
				headers=headers,
				json=payload,
				timeout=provider.timeout_seconds
			)

			response.raise_for_status()
		except requests.exceptions.Timeout as error:
			logger.exception(
				"AI provider request timeout. provider_id=%s provider_url=%s timeout_seconds=%s",
				provider.id,
				provider.provider_url,
				provider.timeout_seconds
			)

			raise AiProviderRequestError("AI provider request timeout.") from error
		except requests.exceptions.RequestException as error:
			logger.exception(
				"AI provider request failed. provider_id=%s provider_url=%s",
				provider.id,
				provider.provider_url
			)

			raise AiProviderRequestError("AI provider request failed.") from error

		response_json = response.json()
		answer_text = self._extract_answer_text(response_json)

		return self._parse_moderation_result(answer_text)

	def _build_user_prompt(
		self,
		request_data: ModerationCheckRequestDto
	) -> str:
		message_lines: list[str] = []

		for message_index, message in enumerate(request_data.messages, start=1):
			if message.name:
				message_lines.append(f'{message_index}. {message.name}: "{message.text}"')
			else:
				message_lines.append(f'{message_index}. "{message.text}"')

		messages_text = "\n".join(message_lines)

		return f"""
Проанализируй фрагмент переписки.

Сообщения:
{messages_text}

Оцени только последнее сообщение с учетом контекста предыдущих сообщений.

Верни результат строго в JSON.
""".strip()

	def _extract_answer_text(
		self,
		response_json: dict
	) -> str:
		try:
			answer_text = response_json["choices"][0]["message"]["content"]
		except (KeyError, IndexError, TypeError) as error:
			logger.error(
				"AI provider returned unexpected response structure. response_json=%s",
				response_json
			)

			raise AiResponseParseError("AI provider returned unexpected response structure.") from error

		if not isinstance(answer_text, str) or not answer_text.strip():
			raise AiResponseParseError("AI provider returned empty answer.")

		return answer_text.strip()

	def _parse_moderation_result(
		self,
		answer_text: str
	) -> ModerationResultDto:
		clean_answer_text = self._extract_json_text(answer_text)

		try:
			answer_json = json.loads(clean_answer_text)
		except json.JSONDecodeError as error:
			logger.error(
				"AI provider returned invalid JSON. answer_text=%s",
				answer_text
			)

			raise AiResponseParseError("AI provider returned invalid JSON.") from error

		try:
			return ModerationResultDto.model_validate(answer_json)
		except ValidationError as error:
			logger.error(
				"AI provider returned JSON with invalid moderation schema. answer_json=%s",
				answer_json
			)

			raise AiResponseValidationError("AI provider returned invalid moderation schema.") from error

	def _extract_json_text(
		self,
		answer_text: str
	) -> str:
		clean_text = answer_text.strip()

		fenced_json_match = re.search(
			r"```(?:json)?\s*(.*?)\s*```",
			clean_text,
			re.DOTALL | re.IGNORECASE
		)

		if fenced_json_match:
			return fenced_json_match.group(1).strip()

		json_object_match = re.search(
			r"\{.*\}",
			clean_text,
			re.DOTALL
		)

		if json_object_match:
			return json_object_match.group(0).strip()

		return clean_text