import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIRECTORY = Path("logs")
APP_LOG_FILE = LOG_DIRECTORY / "app.log"
ERROR_LOG_FILE = LOG_DIRECTORY / "error.log"


def setup_logging() -> None:
	LOG_DIRECTORY.mkdir(exist_ok=True)

	log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
	date_format = "%Y-%m-%d %H:%M:%S"

	root_logger = logging.getLogger()
	root_logger.setLevel(logging.INFO)

	if root_logger.handlers:
		return

	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.INFO)
	console_handler.setFormatter(logging.Formatter(log_format, date_format))

	app_file_handler = RotatingFileHandler(
		APP_LOG_FILE,
		maxBytes=5 * 1024 * 1024,
		backupCount=5,
		encoding="utf-8"
	)
	app_file_handler.setLevel(logging.INFO)
	app_file_handler.setFormatter(logging.Formatter(log_format, date_format))

	error_file_handler = RotatingFileHandler(
		ERROR_LOG_FILE,
		maxBytes=5 * 1024 * 1024,
		backupCount=10,
		encoding="utf-8"
	)
	error_file_handler.setLevel(logging.ERROR)
	error_file_handler.setFormatter(logging.Formatter(log_format, date_format))

	root_logger.addHandler(console_handler)
	root_logger.addHandler(app_file_handler)
	root_logger.addHandler(error_file_handler)