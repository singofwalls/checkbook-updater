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
    rows = sheets_api.get_range(SHEET_NAME)[FIELD_ROW:]

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


def update_entry(entry_num, sheet_entry, bank_entry, fields, accounts):
    """Update the entry in Google Sheets with differing info in the bank entry."""
    values = []
    field_indices = {fields[field]: field for field in fields}
    for i in range(max(field_indices.keys()) + 1):
        if i in field_indices:
            field = field_indices[i]
            values.append(get_value(bank_entry, field, accounts))
        else:
            values.append(None)

    # Indexed from 0, add one for first row
    row = FIELD_ROW + entry_num + 1
    sheets_api.update_cells(f"{SHEET_NAME}!A{row}", [values])


def get_value(bank_entry, sheet_field, accounts):
    """Get the value from the bank entry based on a given sheet field.

    Maps sheet fields to bank fields.
    """
    if sheet_field == "Date":
        return bank_entry["Date"].strftime(DATE_FORMAT)
    elif sheet_field in accounts:
        if bank_entry["account"] == sheet_field:
            return bank_entry["Amount"]
        else:
            return ""
    elif sheet_field == "Bank_Listed_Item":
        return bank_entry["Description"]

    raise Exception(f"Unknown field from sheet: {sheet_field}")