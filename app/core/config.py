from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	app_host: str = "127.0.0.1"
	app_port: int = 18080

	ai_provider_type: str = "openai_compatible"
	ai_provider_url: str = "http://localhost:11434/v1/chat/completions"
	ai_model_name: str = "llama3.1"
	ai_api_key: str = ""
	ai_timeout_seconds: int = 60

	database_url: str

	admin_auth_enabled: bool = True
	admin_username: str = "admin"
	admin_password: str = "admin"
	admin_cookie_secret: str = "ai_moderator_dev_secret"
	admin_session_ttl_seconds: int = 43200
	admin_cookie_secure: bool = False

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore"
	)


settings = Settings()