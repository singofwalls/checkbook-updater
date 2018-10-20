"""Organize old transactions already in the sheet."""

from sheets import get_range


def get_transactions():
    """Pull relevant data and group into discreet transactions."""
    transactions = []
    data = get_range("Sheet1!A6:G")
    for line in filter(lambda line: line[0], data):
        transactions.append([line[0], line[6], line[3], line[4]])
    return transactions
