from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	app_host: str = "127.0.0.1"
	app_port: int = 18080

	ai_provider_type: str = "openai_compatible"
	ai_provider_url: str = "http://localhost:11434/v1/chat/completions"
	ai_model_name: str = "llama3.1"
	ai_api_key: str | None = None
	ai_timeout_seconds: int = 60

	database_url: str = "postgresql+psycopg://ai_moderator_user:ai_moderator_password@localhost:55432/ai_moderator"

	class Config:
		env_file = ".env"


settings = Settings()