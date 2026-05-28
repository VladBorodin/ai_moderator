@echo off
chcp 65001 >nul

setlocal

cd /d "%~dp0"

echo ========================================
echo AI Moderator - запуск приложения
echo ========================================
echo.

if not exist ".venv\Scripts\activate.bat" (
	echo [ERROR] Виртуальное окружение не найдено.
	echo Создай его командой:
	echo python -m venv .venv
	echo.
	pause
	exit /b 1
)

if not exist ".env" (
	echo [WARNING] Файл .env не найден.
	echo Приложение будет использовать значения из config.py.
	echo.
)

echo [INFO] Активация виртуального окружения...
call ".venv\Scripts\activate.bat"

echo [INFO] Проверка Docker Compose...
docker compose version >nul 2>nul

if %errorlevel% equ 0 (
	echo [INFO] Запуск PostgreSQL через Docker Compose...
	docker compose up -d
) else (
	echo [WARNING] Docker Compose не найден.
	echo [WARNING] PostgreSQL должен быть запущен вручную.
)

set APP_HOST=127.0.0.1
set APP_PORT=18080

for /f "tokens=1,* delims==" %%A in (.env) do (
	if "%%A"=="APP_HOST" set APP_HOST=%%B
	if "%%A"=="APP_PORT" set APP_PORT=%%B
)

echo.
echo [INFO] Запуск FastAPI...
echo [INFO] Swagger: http://%APP_HOST%:%APP_PORT%/docs
echo [INFO] Health:  http://%APP_HOST%:%APP_PORT%/health
echo.

uvicorn app.main:app --reload --host %APP_HOST% --port %APP_PORT%

endlocal