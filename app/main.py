from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.ai_provider_settings import router as ai_provider_settings_router
from app.api.moderation import router as moderation_router
from app.api.prompt_templates import router as prompt_templates_router
from app.db.init_db import init_db
from app.web.pages import router as pages_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
	init_db()
	yield


app = FastAPI(
	title="AI Moderator",
	version="0.1.0",
	lifespan=lifespan
)


app.mount(
	"/static",
	StaticFiles(directory="static"),
	name="static"
)

app.include_router(pages_router)
app.include_router(moderation_router)
app.include_router(ai_provider_settings_router)
app.include_router(prompt_templates_router)


@app.get("/health")
def health_check() -> dict[str, str]:
	return {
		"status": "ok"
	}