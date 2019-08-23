"""Handle interactions with the Google Sheet."""
import datetime

import sheets_api
from formatting import format_value

# Constants
ACCOUNT_ROW = 1
FIELD_ROW = 7
SHEET_NAME = "Sheet1"
DATE_FORMAT = "%m/%d/%Y"
RUNNING_FORMULA = f'=IF(ISBLANK(INDIRECT(ADDRESS(ROW(), COLUMN() - 1))), "", sum(indirect(ADDRESS({FIELD_ROW + 1}, COLUMN() - 1)&":"&ADDRESS(ROW(),COLUMN()-1))))'
METHOD_WORDS = {
    "Direct": ("deposit", "ach", "accr earning pymt"),
    "Check": ("check", ),
    "Card": ("pos", "debit", "card"),
}
METHOD_DEFAULT = "Card"


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
    account_row = sheets_api.get_range(f"{SHEET_NAME}!{ACCOUNT_ROW}:{ACCOUNT_ROW}")[0]
    # First cell is "Account": find and skip it
    return account_row[account_row.index("Account") + 1:]


def get_entries(fields, accounts):
    """Get transaction entries already in the sheet."""

    # Pull all entries from sheet
    entries = []
    rows = sheets_api.get_range(SHEET_NAME)[FIELD_ROW:]

    for row in rows:
        entry = {}
        for field_name in fields:
            # Create dict from values in row
            field_num = fields[field_name]
            if field_num >= len(row):
                # Row ends before the extra stuff
                continue
            value = row[field_num]
            entry[field_name] = format_value(value, field_name, DATE_FORMAT)
            # Grab running balance adjacent to account
            if field_name in accounts:
                balance = row[fields[field_name] + 1]
                entry[field_name + " Running"] = format_value(balance)

        # Create transaction from dict
        entries.append(entry)

    return entries


def get_row(entry_index):
    """Return the row in the sheet which corresponds to a given index."""
    return entry_index + FIELD_ROW + 1


def update_entry(entry_num, bank_entry, fields, accounts):
    """Update the entry in Google Sheets with differing info in the bank entry.

    Parameters
    ----------
    entry_num
        None if append to end. Else, row of entry to update.

    """
    values = []

    field_indices = {fields[field]: field for field in fields}
    # Set running to be field to right of account field
    running_index = fields[bank_entry["account"]] + 1
    field_indices[running_index] = "Running"

    for i in range(max(field_indices.keys()) + 1):
        if i in field_indices:
            field = field_indices[i]
            values.append(get_value(bank_entry, field, accounts))
        else:
            values.append(None)

    # Indexed from 0, add one for first row
    if not isinstance(entry_num, type(None)):
        row = get_row(entry_num)
        sheets_api.update_cells(f"{SHEET_NAME}!A{row}", [values])
    else:
        # Point to first row of table, google sheets api will append to end
        row = FIELD_ROW + 1
        sheets_api.append_cells(f"{SHEET_NAME}!A{row}", [values])


def _get_method(description):
    """Determine the method of payment based on the description."""
    for method in METHOD_WORDS:
        for word in METHOD_WORDS[method]:
            if word in description:
                return method
    return METHOD_DEFAULT


def _get_paypal(description):
    """Determine whether payment made via paypal based on description."""
    return ("No", "Yes")["paypal" in description]


def get_value(bank_entry, sheet_field, accounts):
    """Get the value from the bank entry based on a given sheet field.

    Maps sheet fields to bank fields.
    """
    desc = bank_entry["Description"].lower()
    if sheet_field == "Date":
        return bank_entry["Date"].strftime(DATE_FORMAT)
    elif sheet_field in accounts:
        if bank_entry["account"] == sheet_field:
            return bank_entry["Amount"]
        else:
            return ""
    elif sheet_field == "Bank_Listed_Item":
        return bank_entry["Description"]
    elif sheet_field == "Method":
        return _get_method(desc)
    elif sheet_field == "PayPal":
        return _get_paypal(desc)
    elif sheet_field == "In_Account":
        return "Yes"
    elif sheet_field == "Pending":
        if bank_entry["Transaction Status"] == "Pending transaction":
            return "Yes"
        return "No"
    elif "Running" in sheet_field:
        if sheet_field == bank_entry["account"] + " Running":
            # This occurs when called from print_match and is printed to console
            return bank_entry["Balance"]
        elif sheet_field == "Running":
            # This occurs when called from update_entry and goes in the sheet
            return RUNNING_FORMULA
        else:
            # This occurs from print_match.
            # For runnings which are not the current account
            return ""

    raise Exception(f"Unknown field from sheet: {sheet_field}")


def add_bank_balance(amount, account, accounts):
    """Add the bank's reported amount to the sheet."""
    row = ACCOUNT_ROW + 3
    values = [None] * len(accounts)
    values[accounts.index(account)] = amount
    sheets_api.update_cells(f"{SHEET_NAME}!B{row}", [values])


def add_entries(entries, fields, accounts):
    """Add new entries to the spreadsheet."""

    for entry in entries:
        update_entry(None, entry, fields, accounts)


def update_timestamp():
    """Update the timestamp on the sheet."""
    timestamp = datetime.datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
    sheets_api.update_cells(f"{SHEET_NAME}!B{FIELD_ROW - 1}", [[timestamp]])
