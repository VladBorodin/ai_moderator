import json
from typing import Any

import requests


class AiModerationService:
	def __init__(
		self,
		provider_url: str,
		model_name: str,
		api_key: str | None,
		timeout_seconds: int
	) -> None:
		self.provider_url = provider_url
		self.model_name = model_name
		self.api_key = api_key
		self.timeout_seconds = timeout_seconds

	def moderate(self, request_data: dict[str, Any]) -> dict[str, Any]:
		system_prompt = self._build_system_prompt()
		user_prompt = self._build_user_prompt(request_data)

		headers = {
			"Content-Type": "application/json"
		}

		if self.api_key:
			headers["Authorization"] = f"Bearer {self.api_key}"

		payload = {
			"model": self.model_name,
			"messages": [
				{
					"role": "system",
					"content": system_prompt
				},
				{
					"role": "user",
					"content": user_prompt
				}
			],
			"temperature": 0.1
		}

		response = requests.post(
			self.provider_url,
			headers=headers,
			json=payload,
			timeout=self.timeout_seconds
		)

		response.raise_for_status()

		response_json = response.json()
		answer_text = response_json["choices"][0]["message"]["content"]

		return self._parse_answer(answer_text)

	def _build_user_prompt(self, request_data: dict[str, Any]) -> str:
		trigger_word = request_data.get("trigger_word", "")
		messages = request_data.get("messages", [])

		message_lines: list[str] = []

		for message_index, message in enumerate(messages, start=1):
			author_name = message.get("name", "Неизвестный")
			message_text = message.get("text", "")
			message_lines.append(f'{message_index}. {author_name}: "{message_text}"')

		messages_text = "\n".join(message_lines)

		return f"""
Проанализируй переписку.

Триггерное слово:
"{trigger_word}"

Сообщения:
{messages_text}

Оцени только последнее сообщение с учетом контекста.
Верни результат строго в JSON.
""".strip()

	def _parse_answer(self, answer_text: str) -> dict[str, Any]:
		try:
			model_result = json.loads(answer_text)
		except json.JSONDecodeError:
			return self._create_fallback_result("Модель вернула невалидный JSON.")

		verdict = model_result.get("verdict")
		offense_level = model_result.get("offense_level")
		description = model_result.get("description")

		if verdict not in [0, 1]:
			return self._create_fallback_result("Модель вернула некорректное значение verdict.")

		if not isinstance(offense_level, int) or offense_level < 0 or offense_level > 10:
			return self._create_fallback_result("Модель вернула некорректное значение offense_level.")

		if not isinstance(description, str) or not description.strip():
			return self._create_fallback_result("Модель вернула пустое описание.")

		return {
			"verdict": verdict,
			"offense_level": offense_level,
			"description": description.strip()
		}

	def _create_fallback_result(self, description: str) -> dict[str, Any]:
		return {
			"verdict": 1,
			"offense_level": 5,
			"description": f"Требуется ручная проверка. Причина: {description}"
		}

	def _build_system_prompt(self) -> str:
		return """
Ты являешься ИИ-модератором переписки.

Твоя задача - оценить только последнее сообщение в контексте предыдущих сообщений.

В последнем сообщении есть триггерное слово или выражение.
Наличие триггерного слова НЕ означает автоматически нарушение.

Ты должен определить, используется ли это слово или выражение в уничижительном, оскорбительном, травящем, дискриминационном, агрессивном или враждебном контексте.

Важно:
1. Оценивай не слово само по себе, а смысл последнего сообщения в контексте переписки.
2. Учитывай, что собеседники могут быть друзьями и могут подшучивать друг над другом.
3. Учитывай, что слово может использоваться как цитата, самоирония, обсуждение самого слова или нейтральное географическое/историческое/культурное название.
4. Если слово присутствует, но контекст нейтральный, дружеский или не уничижительный - это не нарушение.
5. Если сообщение направлено на унижение, травлю, оскорбление или враждебность - это нарушение.
6. Если контекста недостаточно для уверенного вывода, выбирай мягкую оценку и объясняй сомнение в description.

Верни строго JSON без markdown.

Формат ответа:
{
	"verdict": 0 или 1,
	"offense_level": число от 0 до 10,
	"description": "короткий вывод на русском языке"
}

Правила:
- verdict = 0, если оскорбительного или уничижительного контекста нет.
- verdict = 1, если оскорбительный или уничижительный контекст есть.
- offense_level = 0, если контекст полностью нейтральный.
- offense_level = 1-3, если есть грубость или спорный тон, но явного унижения нет.
- offense_level = 4-6, если есть оскорбление.
- offense_level = 7-8, если есть явное унижение, травля или враждебность.
- offense_level = 9-10, если есть жесткая дегуманизация, угроза, призыв к насилию или сильная ненависть.
""".strip()