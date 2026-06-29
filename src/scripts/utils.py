from datetime import datetime

def parse_legacy_date(date_str):
    """
    Converts legacy 'dYYYYMMDD' or 'mYYYYMM' strings to Python date objects.
    Returns None if invalid.
    """
    if not isinstance(date_str, str):
        return None
        
    # Standard Day: d20250101
    if len(date_str) == 9 and date_str.startswith("d"):
        try:
            return datetime.strptime(date_str, "d%Y%m%d").date()
        except ValueError:
            return None

    # Month Code: m202501 (Sometimes used for 'valid_from' etc?)
    if len(date_str) == 7 and date_str.startswith("m"):
        try:
            # Return 1st of month
            return datetime.strptime(date_str, "m%Y%m").date()
        except ValueError:
            return None
            
    return None