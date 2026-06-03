from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.dashboard_statistics_service import DashboardStatisticsService


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