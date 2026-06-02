DEFAULT_SYSTEM_SETTINGS = [
	{
		"code": "moderation.store_full_request_json",
		"value": "true",
		"description": "Store full incoming moderation request JSON in moderation_log."
	},
	{
		"code": "moderation.store_full_response_json",
		"value": "true",
		"description": "Store full AI moderation response JSON in moderation_log."
	},
	{
		"code": "moderation.log_retention_days",
		"value": "120",
		"description": "How many days moderation logs should be kept before cleanup."
	},
	{
		"code": "ai.temperature",
		"value": "0.1",
		"description": "Default AI model temperature for moderation requests."
	},
	{
		"code": "ai.max_tokens",
		"value": "512",
		"description": "Default maximum output tokens for AI moderation response."
	}
]