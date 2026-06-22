from datetime import date, timedelta
from typing import Optional

def parse_dates(start_date: Optional[date], end_date: Optional[date], interval: str = "month") -> tuple[date, date]:
    parsed_end = end_date if (end_date is not None) else date.today()
    
    if start_date is None:
        default_days = 84 if interval == "week" else 365 # 12 weeks or 12 months
        parsed_start = start_date if (start_date is not None) else parsed_end - timedelta(days=default_days)
    return parsed_start, parsed_end