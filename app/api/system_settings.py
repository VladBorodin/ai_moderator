from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.system_setting import SystemSettingDto, SystemSettingUpdateDto
from app.services.system_setting_service import SystemSettingService


router = APIRouter(
	prefix="/settings/system-settings",
	tags=["System Settings"]
)


@router.get("", response_model=list[SystemSettingDto])
def get_system_settings(
	db: Session = Depends(get_db)
) -> list[SystemSettingDto]:
	service = SystemSettingService(db)

	return service.get_all()


@router.get("/{code}", response_model=SystemSettingDto)
def get_system_setting(
	code: str,
	db: Session = Depends(get_db)
) -> SystemSettingDto:
	service = SystemSettingService(db)
	setting = service.get_by_code(code)

	if setting is None:
		raise HTTPException(
			status_code=404,
			detail="System setting was not found."
		)

	return setting


@router.put("/{code}", response_model=SystemSettingDto)
def update_system_setting(
	code: str,
	dto: SystemSettingUpdateDto,
	db: Session = Depends(get_db)
) -> SystemSettingDto:
	service = SystemSettingService(db)
	setting = service.update_by_code(
		code=code,
		dto=dto
	)

	if setting is None:
		raise HTTPException(
			status_code=404,
			detail="System setting was not found."
		)

	return setting