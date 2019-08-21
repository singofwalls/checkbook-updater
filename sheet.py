"""Handle interactions with the Google Sheet."""
import sheets_api
from formatting import format_value

# Constants
ACCOUNT_ROW = 1
FIELD_ROW = 5
SHEET_NAME = "Sheet1"
DATE_FORMAT = "%m/%d/%Y"


def get_fields():
    """Pull the fields from the sheet with asterisks at the end."""
    # get_range returns list of rows. Only one row being asked for: access that one
    all_fields = sheets_api.get_range(f"{SHEET_NAME}!{FIELD_ROW}:{FIELD_ROW}")[0]

    # Find cells ending with * and associate with column num in fields dict
    fields = filter(lambda f: f.endswith("*"), all_fields)
    fields = {
        field.replace(" ", "_").replace("*", ""): all_fields.index(field)
        for field in fields
    }

    return fields


def get_accounts():
    """Get the names of the accounts."""
    account_row = sheets_api.get_range(f"{SHEET_NAME}!{ACCOUNT_ROW}2:{ACCOUNT_ROW}")[0]
    # First cell is "Account": skip it
    return account_row[1:]


def get_entries(fields, accounts):
    """Get transaction entries already in the sheet."""

    # Pull all entries from sheet
    entries = []
    rows = sheets_api.get_range(SHEET_NAME)[FIELD_ROW + 1 :]

    for row in rows:
        entry = {}
        for field_name in fields:
            # Create dict from values in row
            value = row[fields[field_name]]
            entry[field_name] = format_value(value, field_name, DATE_FORMAT)
            # Grab running balance adjacent to account
            if field_name in accounts:
                balance = row[fields[field_name] + 1]
                entry[field_name + " Running"] = format_value(balance)

        # Create transaction from dict
        entries.append(entry)

    return entries