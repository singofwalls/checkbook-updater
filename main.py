"""A rewrite of the banking script."""
from string import ascii_uppercase
from datetime import timedelta

import sheets_api
import sheet
import bank

from formatting import format_desc

MATCH_WEIGHTS = {
    "date diff": 5,
    "amount diff": 10,
    "balance diff": 1,
    "desc": 50,
    "desc update": 0,
}


def _get_match_factors(sheet_entry, bank_entry, accounts):
    """Get the factors which contribute to a match."""

    factors = {}

    factors["date diff"] = bank_entry["Date"] - sheet_entry["Date"]

    # Find amount which isn't blank for this entry
    for account in accounts:
        sheet_amount = sheet_entry[account]
        sheet_balance = sheet_entry[account + " Running"]
        if sheet_amount:
            break

    factors["amount diff"] = bank_entry["Amount"] - sheet_amount

    bank_balance = bank_entry["Balance"]

    factors["balance diff"] = None
    if bank_balance != "":
        factors["balance diff"] = bank_balance - sheet_balance

    sheet_desc = sheet_entry["Bank_Listed_Item"]
    bank_desc = bank_entry["Description"]

    factors["desc"] = format_desc(sheet_desc) == format_desc(bank_desc)
    factors["desc update"] = sheet_desc != bank_desc

    return factors


def score_match(sheet_entry, bank_entry, accounts):
    """Produce a score based on the factors which contribute to a match and 
    their weights.
    """



def find_new_entries(sheet_entries, bank_entries, accounts):
    """Find all entries not already in the sheet."""

    def entry_key(entry):
        return entry["Date"]

    # Sort entries by date
    sheet_entries = sorted(sheet_entries, key=entry_key)
    bank_entries = sorted(bank_entries, key=entry_key)

    for sheet_entry in sheet_entries:
        for bank_entry in bank_entries:
            print(_get_match_factors(sheet_entry, bank_entry, accounts))


def main():
    sheets_api.authorize()

    accounts = sheet.get_accounts()

    sheet_fields = sheet.get_fields()
    sheet_entries = sheet.get_entries(sheet_fields, accounts)

    bank_fields = bank.get_fields()
    bank_entries = bank.get_entries(bank_fields)

    new_entries = find_new_entries(sheet_entries, bank_entries, accounts)


if __name__ == "__main__":
    main()
