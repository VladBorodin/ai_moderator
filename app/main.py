from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from app.api.moderation import router as moderation_router
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
	init_db()
	yield


app = FastAPI(
	title="AI Moderator",
	version="0.1.0",
	lifespan=lifespan
)


app.include_router(moderation_router)


@app.get("/health")
def health_check() -> dict[str, str]:
	return {
		"status": "ok"
	}