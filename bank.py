"""Handle interactions with the txt from the bank.

This txt can be made by copy and pasting the transaction log on a specific account's
page. Copy at least as far back as the start of the previous upload to ensure
no gaps exist in the checkbook sheet. Ensure first row includes field names.
"""
import os

from formatting import format_value


# Constants
FILE_PATH = "accounts/"
DATE_FORMAT = "%b %d, %Y"


def get_fields():
    """Get fields from bank's txt."""
    os.chdir(FILE_PATH)
    files = os.listdir()

    # Open first file to pull field names
    with open(files[0]) as file:
        field_line = file.readline()

    fields = field_line.split("\t")
    fields = list(map(lambda f: f.strip(), fields))

    # Easy to accidentally copy this invisible header with no corresponding values
    # Remove it if present
    if fields[0] == "Transaction Status":
        fields = fields[1:]

    fields = {field: num for num, field in enumerate(fields)}

    return fields


def _get_entries_from_file(fields, content):
    """Get entries from file content."""
    # Remove header line
    raw_lines = content.split("\n")[1:]
    entries = []

    for num, line in enumerate(raw_lines):
        if num % 2:
            # Refactor date lines onto start of following line and split tabs
            values = (raw_lines[num - 1] + line).split("\t")

            entry = {}
            for field_name in fields:
                field_num = fields[field_name]
                value = values[field_num]
                entry[field_name] = format_value(value, field_name, DATE_FORMAT)

            entries.append(entry)

    return entries


def get_entries(fields):
    """Organize entries from txts."""
    entries = []

    for file_name in os.listdir():
        with open(file_name) as file:
            account_entries = _get_entries_from_file(fields, file.read())

            # Add account name to entries
            for num in range(len(account_entries)):
                account_entries[num]["account"] = file_name[: -len(".txt")]

            entries.extend(account_entries)

    return entries
