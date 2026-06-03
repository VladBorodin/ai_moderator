DEFAULT_SYSTEM_SETTINGS = [
	{
		"code": "moderation.store_full_request_json",
		"value": "true",
		"description": "Сохранять полный входящий JSON запроса в журнале проверок."
	},
	{
		"code": "moderation.store_full_response_json",
		"value": "true",
		"description": "Сохранять полный JSON ответа ИИ в журнале проверок."
	},
	{
		"code": "moderation.log_retention_days",
		"value": "120",
		"description": "Сколько дней хранить записи журнала проверок перед очисткой."
	},
	{
		"code": "ai.temperature",
		"value": "0.1",
		"description": "Температура модели при запросе модерации. Чем ниже значение, тем стабильнее ответ."
	},
	{
		"code": "ai.max_tokens",
		"value": "512",
		"description": "Максимальное количество токенов в ответе ИИ для результата модерации."
	}
]