from pydantic import BaseModel

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.admin_auth import (
	clear_admin_auth_cookie,
	set_admin_auth_cookie,
	verify_admin_credentials
)


router = APIRouter(
	tags=["Admin Auth"]
)

templates = Jinja2Templates(directory="templates")


class AdminLoginRequestDto(BaseModel):
	username: str
	password: str


@router.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request) -> HTMLResponse:
	return templates.TemplateResponse(
		request=request,
		name="login.html",
		context={
			"page_title": "Вход"
		}
	)


@router.post("/login")
def login(dto: AdminLoginRequestDto) -> JSONResponse:
	if not verify_admin_credentials(
		username=dto.username,
		password=dto.password
	):
		return JSONResponse(
			status_code=401,
			content={
				"detail": "Неверный логин или пароль."
			}
		)

	response = JSONResponse(
		content={
			"success": True,
			"redirect_url": "/"
		}
	)

	set_admin_auth_cookie(
		response=response,
		username=dto.username
	)

	return response


@router.post("/logout")
def logout() -> RedirectResponse:
	response = RedirectResponse(
		url="/login",
		status_code=303
	)

	clear_admin_auth_cookie(response)

	return response