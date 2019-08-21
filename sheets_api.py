"""Handle Google Sheet API and functionality."""
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# If modifying these scopes, delete the file token.json.
SCOPES = "https://www.googleapis.com/auth/spreadsheets"

# The ID and range of a sample spreadsheet.
with open("sheet_ID.txt") as sheet_file:
    SPREADSHEET_ID = sheet_file.read().strip("\n")

service = None


def authorize():
    """Authorize the script to access the sheet."""
    global service

    store = file.Storage("token.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("credentials.json", SCOPES)
        creds = tools.run_flow(flow, store)
    service = build("sheets", "v4", http=creds.authorize(Http()))


def get_range(range_name):
    """Return a range of values."""
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=range_name)
        .execute()
    )
    return result.get("values", [])


def append_cells(range_name, values):
    """Append values to cells in the given range."""
    body = {"values": values}
    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        )
        .execute()
    )
    return result


def update_cells(range_name, values):
    """Update values for cells in the given range."""
    body = {"values": values}
    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        )
        .execute()
    )
    return result
