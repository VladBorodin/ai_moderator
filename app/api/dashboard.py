from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.dashboard_statistics_service import DashboardStatisticsService
from datetime import datetime


router = APIRouter(
	prefix="/dashboard",
	tags=["Dashboard"]
)


@router.get("/statistics")
def get_dashboard_statistics(
	days: int = Query(default=14, ge=1, le=90),
	db: Session = Depends(get_db)
) -> dict[str, Any]:
	service = DashboardStatisticsService(db)

	return service.get_statistics(days=days)

@router.get("/statistics/day/{date_text}")
def get_dashboard_day_statistics(
	date_text: str,
	db: Session = Depends(get_db)
) -> dict[str, Any]:
	try:
		datetime.strptime(date_text, "%Y-%m-%d")
	except ValueError as error:
		raise HTTPException(
			status_code=400,
			detail="Date must be in YYYY-MM-DD format."
		) from error

	service = DashboardStatisticsService(db)

	return service.get_day_statistics(date_text=date_text)