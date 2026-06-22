from datetime import date, timedelta
from typing import Optional

from src.core.utils.date_helper import parse_dates

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.core.database import get_db

from src.modules.dashboard.service import GetDashboardGeneral

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/")
def get_general(
    db: Session = Depends(get_db),
    start_date: Optional[date] = Query(None, description="Start date of the timeframe (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date of the timeframe (YYYY-MM-DD)"),
    interval: str = Query("month", pattern="^(month|week)$", description="Aggregation interval ('month' or 'week')")
):
    parsed_start, parsed_end = parse_dates(start_date, end_date, interval)
    action = GetDashboardGeneral(
        db,
        start_date=parsed_start,
        end_date=parsed_end,
        interval=interval
    )
    return action.execute()


@router.get("/team")
def get_team_stats(
    db: Session = Depends(get_db),
    emp_ids: list[str] = Query(..., description="List of employee IDs for the team statistics"),
    start_date: Optional[date] = Query(None, description="Start date of the timeframe (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date of the timeframe (YYYY-MM-DD)"),
    interval: str = Query("month", pattern="^(month|week)$", description="Aggregation interval ('month' or 'week')")
):
    parsed_start, parsed_end = parse_dates(start_date, end_date, interval)
    action = GetDashboardGeneral(
        db, 
        emp_ids=emp_ids, 
        start_date=parsed_start, 
        end_date=parsed_end,
        interval=interval
    )
    return action.execute()