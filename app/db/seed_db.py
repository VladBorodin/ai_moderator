import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.default_prompts import (
	DEFAULT_MODERATION_PROMPT_CODE,
	DEFAULT_MODERATION_PROMPT_NAME,
	DEFAULT_MODERATION_PROMPT_TEXT,
	DEFAULT_MODERATION_PROMPT_VERSION
)
from app.core.default_settings import DEFAULT_SYSTEM_SETTINGS
from app.models.prompt_template import PromptTemplate
from app.models.system_setting import SystemSetting


logger = logging.getLogger(__name__)


def seed_db(db: Session) -> None:
	seed_system_settings(db)
	seed_default_prompt(db)


def seed_system_settings(db: Session) -> None:
	for setting_data in DEFAULT_SYSTEM_SETTINGS:
		statement = select(SystemSetting).where(SystemSetting.code == setting_data["code"])
		existing_setting = db.scalars(statement).first()

		if existing_setting is not None:
			continue

		system_setting = SystemSetting(
			code=setting_data["code"],
			value=setting_data["value"],
			description=setting_data["description"]
		)

		db.add(system_setting)

	db.commit()


def seed_default_prompt(db: Session) -> None:
	statement = (
		select(PromptTemplate)
		.where(PromptTemplate.code == DEFAULT_MODERATION_PROMPT_CODE)
		.where(PromptTemplate.is_deleted.is_(False))
	)

	existing_prompt = db.scalars(statement).first()

	if existing_prompt is not None:
		return

	active_prompt_statement = (
		select(PromptTemplate)
		.where(PromptTemplate.is_active.is_(True))
		.where(PromptTemplate.is_deleted.is_(False))
	)

	active_prompt = db.scalars(active_prompt_statement).first()

	default_prompt = PromptTemplate(
		code=DEFAULT_MODERATION_PROMPT_CODE,
		name=DEFAULT_MODERATION_PROMPT_NAME,
		prompt_text=DEFAULT_MODERATION_PROMPT_TEXT,
		version=DEFAULT_MODERATION_PROMPT_VERSION,
		is_active=active_prompt is None
	)

	db.add(default_prompt)
	db.commit()

	logger.info("Default moderation prompt was created.")