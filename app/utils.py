import re
from datetime import datetime
from typing import Dict

def validate_phone(phone: str) -> bool:
    """Validates 10-digit Indian phone numbers as per assignment requirements."""
    return bool(re.fullmatch(r'^[6-9]\d{9}$', ''.join(filter(str.isdigit, phone))))

def validate_date(date_str: str) -> bool:
    """Validates date strings in YYYY-MM-DD format (ISO 8601)."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_time(time_str: str) -> bool:
    """Validates time strings in HH:MM format (24-hour clock)."""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def normalize_date(date_str: str) -> str:
    """Converts dates to YYYY-MM-DD or 'NA' per Postcall-configuration.pdf."""
    if validate_date(date_str):
        return date_str
    return "NA"


def normalize_time(time_str: str) -> str:
    """Converts time inputs to HH:MM (24h) or 'NA' per requirements."""
    for fmt in ("%H:%M", "%I:%M %p", "%I:%M%p"):
        try:
            dt = datetime.strptime(time_str, fmt)
            return dt.strftime("%H:%M")
        except ValueError:
            continue
    return "NA"


def confirm_entity(entity_name: str, entity_value: str) -> str:
    """Generates confirmation prompts following [master_collect.pdf] template."""
    return f"So, just to confirm, your {entity_name} is {entity_value}, correct?"


