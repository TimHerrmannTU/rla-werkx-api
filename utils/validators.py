from typing import Optional, Annotated
from datetime import date, datetime
from pydantic import BeforeValidator

def parse_legacy_date(v):
    if v is None: return None
    if isinstance(v, date): return v
    if isinstance(v, str) and v.startswith("d") and len(v) == 9:
        try:
            return datetime.strptime(v, "d%Y%m%d").date()
        except ValueError:
            return None
    return None
LegacyDate = Annotated[Optional[date], BeforeValidator(parse_legacy_date)]