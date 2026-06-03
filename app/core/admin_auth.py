import hashlib
import hmac
import os
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response


ADMIN_AUTH_COOKIE_NAME = "ai_moderator_admin_auth"


PUBLIC_EXACT_PATHS = {
	"/login",
	"/health",
	"/favicon.ico"
}

PUBLIC_PREFIXES = (
	"/static",
)

PROTECTED_EXACT_PATHS = {
	"/",
	"/docs",
	"/redoc",
	"/openapi.json"
}

PROTECTED_PREFIXES = (
	"/dashboard",
	"/moderation-test",
	"/moderation-logs",
	"/ai-provider-settings",
	"/prompt-settings",
	"/system-logs",
	"/system-settings",
	"/settings",
	"/api/system-logs",
	"/moderation/logs"
)


def register_admin_auth_middleware(app: FastAPI) -> None:
	@app.middleware("http")
	async def admin_auth_middleware(
		request: Request,
		call_next: Callable[[Request], Awaitable[Response]]
	) -> Response:
		if not _requires_admin_auth(request):
			return await call_next(request)

		if is_admin_authenticated(request):
			return await call_next(request)

		if _wants_html(request):
			return RedirectResponse(
				url="/login",
				status_code=303
			)

		return JSONResponse(
			status_code=401,
			content={
				"detail": "Admin authentication required."
			}
		)


def is_admin_auth_enabled() -> bool:
	value = os.getenv("ADMIN_AUTH_ENABLED", "true").strip().lower()

	return value not in ["false", "0", "no", "n"]


def verify_admin_credentials(
	username: str,
	password: str
) -> bool:
	expected_username = os.getenv("ADMIN_USERNAME", "admin")
	expected_password = os.getenv("ADMIN_PASSWORD", "admin")

	return (
		hmac.compare_digest(username, expected_username)
		and hmac.compare_digest(password, expected_password)
	)


def create_admin_auth_token(username: str) -> str:
	expires_at = int(time.time()) + _get_session_ttl_seconds()
	payload = f"{username}:{expires_at}"
	signature = _sign_payload(payload)

	return f"{payload}:{signature}"


def is_admin_authenticated(request: Request) -> bool:
	if not is_admin_auth_enabled():
		return True

	token = request.cookies.get(ADMIN_AUTH_COOKIE_NAME)

	if not token:
		return False

	parts = token.split(":")

	if len(parts) != 3:
		return False

	username = parts[0]
	expires_at_text = parts[1]
	signature = parts[2]

	try:
		expires_at = int(expires_at_text)
	except ValueError:
		return False

	if expires_at < int(time.time()):
		return False

	expected_username = os.getenv("ADMIN_USERNAME", "admin")

	if not hmac.compare_digest(username, expected_username):
		return False

	payload = f"{username}:{expires_at}"
	expected_signature = _sign_payload(payload)

	return hmac.compare_digest(signature, expected_signature)


def set_admin_auth_cookie(
	response: Response,
	username: str
) -> None:
	token = create_admin_auth_token(username)

	response.set_cookie(
		key=ADMIN_AUTH_COOKIE_NAME,
		value=token,
		max_age=_get_session_ttl_seconds(),
		httponly=True,
		samesite="lax",
		secure=_is_cookie_secure()
	)


def clear_admin_auth_cookie(response: Response) -> None:
	response.delete_cookie(
		key=ADMIN_AUTH_COOKIE_NAME
	)


def _requires_admin_auth(request: Request) -> bool:
	if not is_admin_auth_enabled():
		return False

	path = request.url.path

	if path in PUBLIC_EXACT_PATHS:
		return False

	for public_prefix in PUBLIC_PREFIXES:
		if path.startswith(public_prefix):
			return False

	if path in PROTECTED_EXACT_PATHS:
		return True

	for protected_prefix in PROTECTED_PREFIXES:
		if path.startswith(protected_prefix):
			return True

	return False


def _wants_html(request: Request) -> bool:
	accept_header = request.headers.get("accept", "")

	return "text/html" in accept_header


def _sign_payload(payload: str) -> str:
	secret = os.getenv("ADMIN_COOKIE_SECRET", "ai_moderator_dev_secret")

	return hmac.new(
		key=secret.encode("utf-8"),
		msg=payload.encode("utf-8"),
		digestmod=hashlib.sha256
	).hexdigest()


def _get_session_ttl_seconds() -> int:
	value = os.getenv("ADMIN_SESSION_TTL_SECONDS", "43200")

	try:
		return int(value)
	except ValueError:
		return 43200


def _is_cookie_secure() -> bool:
	value = os.getenv("ADMIN_COOKIE_SECURE", "false").strip().lower()

	return value in ["true", "1", "yes", "y"]