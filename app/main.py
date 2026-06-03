import logging

from app.api.dashboard import router as dashboard_router
from app.core.logging_config import setup_logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.system_settings import router as system_settings_router
from app.api.ai_provider_settings import router as ai_provider_settings_router
from app.api.moderation import router as moderation_router
from app.api.prompt_templates import router as prompt_templates_router
from app.api.system_logs import router as system_logs_router
from app.api.admin_auth import router as admin_auth_router
from app.core.admin_auth import register_admin_auth_middleware
from app.db.init_db import init_db
from app.web.pages import router as pages_router



logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
	setup_logging()
	logger.info("Starting AI Moderator application.")
	init_db()
	logger.info("Database initialization completed.")
	yield
	logger.info("Stopping AI Moderator application.")


app = FastAPI(
	title="AI Moderator",
	version="0.1.0",
	lifespan=lifespan
)

register_admin_auth_middleware(app)

app.mount(
	"/static",
	StaticFiles(directory="static"),
	name="static"
)

app.include_router(pages_router)
app.include_router(moderation_router)
app.include_router(ai_provider_settings_router)
app.include_router(prompt_templates_router)
app.include_router(system_logs_router)
app.include_router(dashboard_router)
app.include_router(system_settings_router)
app.include_router(admin_auth_router)


@app.get("/health")
def health_check() -> dict[str, str]:
	return {
		"status": "ok"
	}
