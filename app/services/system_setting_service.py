from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.system_setting import SystemSetting


class SystemSettingService:
	def __init__(self, db: Session) -> None:
		self.db = db

	def get_value(
		self,
		code: str,
		default_value: str | None = None
	) -> str | None:
		statement = (
			select(SystemSetting)
			.where(SystemSetting.code == code)
		)

		setting = self.db.scalars(statement).first()

		if setting is None:
			return default_value

		return setting.value

	def get_float(
		self,
		code: str,
		default_value: float
	) -> float:
		value = self.get_value(code)

		if value is None:
			return default_value

		try:
			return float(value)
		except ValueError:
			return default_value

	def get_int(
		self,
		code: str,
		default_value: int
	) -> int:
		value = self.get_value(code)

		if value is None:
			return default_value

		try:
			return int(value)
		except ValueError:
			return default_value

	def get_bool(
		self,
		code: str,
		default_value: bool
	) -> bool:
		value = self.get_value(code)

		if value is None:
			return default_value

		normalized_value = value.strip().lower()

		if normalized_value in ["true", "1", "yes", "y"]:
			return True

		if normalized_value in ["false", "0", "no", "n"]:
			return False

		return default_value