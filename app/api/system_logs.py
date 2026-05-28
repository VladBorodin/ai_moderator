from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.core.logging_config import APP_LOG_FILE, ERROR_LOG_FILE


router = APIRouter(
	prefix="/system-logs",
	tags=["System Logs"]
)


@router.get("")
def get_system_logs(
	lines: int = Query(default=200, ge=1, le=2000)
) -> dict[str, list[str]]:
	return {
		"app_log": _read_last_lines(APP_LOG_FILE, lines),
		"error_log": _read_last_lines(ERROR_LOG_FILE, lines)
	}


@router.get("/download/{log_type}")
def download_system_log(log_type: str) -> FileResponse:
	log_file = _get_log_file_by_type(log_type)

	if not log_file.exists():
		raise HTTPException(
			status_code=404,
			detail="Log file was not found."
		)

	return FileResponse(
		path=log_file,
		filename=log_file.name,
		media_type="text/plain"
	)


def _get_log_file_by_type(log_type: str) -> Path:
	if log_type == "app":
		return APP_LOG_FILE

	if log_type == "error":
		return ERROR_LOG_FILE

	raise HTTPException(
		status_code=400,
		detail="Unknown log type."
	)


def _read_last_lines(
	file_path: Path,
	lines_count: int
) -> list[str]:
	if not file_path.exists():
		return []

	with file_path.open("r", encoding="utf-8", errors="replace") as log_file:
		lines = log_file.readlines()

	return [line.rstrip("\n") for line in lines[-lines_count:]]