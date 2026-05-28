from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
	tags=["Admin UI"]
)

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def get_index_page(request: Request) -> HTMLResponse:
	return templates.TemplateResponse(
		request=request,
		name="index.html",
		context={
			"page_title": "Dashboard",
			"active_page": "dashboard"
		}
	)


@router.get("/moderation-test", response_class=HTMLResponse)
def get_moderation_test_page(request: Request) -> HTMLResponse:
	return templates.TemplateResponse(
		request=request,
		name="moderation_test.html",
		context={
			"page_title": "Проверка сообщения",
			"active_page": "moderation_test"
		}
	)


@router.get("/moderation-logs", response_class=HTMLResponse)
def get_moderation_logs_page(request: Request) -> HTMLResponse:
	return templates.TemplateResponse(
		request=request,
		name="moderation_logs.html",
		context={
			"page_title": "Журнал проверок",
			"active_page": "moderation_logs"
		}
	)

@router.get("/ai-provider-settings", response_class=HTMLResponse)
def get_ai_provider_settings_page(request: Request) -> HTMLResponse:
	return templates.TemplateResponse(
		request=request,
		name="ai_provider_settings.html",
		context={
			"page_title": "Настройки ИИ",
			"active_page": "ai_provider_settings"
		}
	)

@router.get("/prompt-settings", response_class=HTMLResponse)
def get_prompt_settings_page(request: Request) -> HTMLResponse:
	return templates.TemplateResponse(
		request=request,
		name="prompt_settings.html",
		context={
			"page_title": "Промты",
			"active_page": "prompt_settings"
		}
	)

@router.get("/system-logs", response_class=HTMLResponse)
def get_system_logs_page(request: Request) -> HTMLResponse:
	return templates.TemplateResponse(
		request=request,
		name="system_logs.html",
		context={
			"page_title": "Системные логи",
			"active_page": "system_logs"
		}
	)