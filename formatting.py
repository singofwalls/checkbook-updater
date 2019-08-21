"""Handle formatting of entries."""
from datetime import datetime
import re

PENDING_TAG = "Memo Post"


def is_num(value):
    """Determine whether a datum is a number."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def format_value(value, field="", date_format=""):
    """Format as date, number, or original."""
    if field == "Date":
        return datetime.strptime(value, date_format)
    else:
        num_val = re.sub("[,$]", "", value)
        if is_num(num_val):
            return float(num_val)

    return value
