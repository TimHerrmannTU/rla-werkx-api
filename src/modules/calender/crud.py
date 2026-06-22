from sqlalchemy import extract
from sqlalchemy.orm import Session, joinedload
from typing import Sequence
from datetime import date
# custom modules
from src.modules.calender.model import CalendarDay, Holiday

def get_calendar_days(db: Session, year: int, month: int = None) -> Sequence[CalendarDay]:
    
    # get days of a entire year or a specific month
    filters = [
        extract('year', CalendarDay.date) == year
    ]    
    if month: filters.append( extract('month', CalendarDay.date) == month) 

    return (
        db.query(
            CalendarDay
        ).options(
            joinedload(CalendarDay.holiday).joinedload(Holiday.location)
        ).filter(
            *filters
        ).order_by(
            CalendarDay.date
        ).all()
    )
    
def get_calendar_days_within_range(db: Session, start_date: date, end_date: date) -> Sequence[CalendarDay]:
    return (
        db.query(
            CalendarDay
        ).options(
            joinedload(CalendarDay.holiday)
        ).filter(
            CalendarDay.date >= start_date, 
            CalendarDay.date < end_date
        ).order_by(
            CalendarDay.date
        ).all()
    )