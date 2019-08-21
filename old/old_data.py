"""Organize old transactions already in the sheet."""

from sheets import get_range, write_cells


def get_transactions():
    """Pull relevant data and group into discreet transactions."""
    transactions = []
    data = get_range("Sheet1!A6:G")
    for line in filter(lambda line: line[0], data):
        transactions.append([line[0], line[6], line[3], line[4]])
    return transactions


def add_transactions(transactions, index):
    """Update transactions in sheet with new transactions.
    
    Parameters
    ----------
    transactions
        A list of transactions to be added to the sheet.
    index
        The index of the first transaction with respect to the transactions already 
        on the sheet.

    """

    def get_medium(description):
        """Determine what method was used to pay, rudimentally."""
        description = description.lower()
        if "deposit" in description:
            return "Direct"
        if "check" in description:
            return "Check"
        return "Card"

    def format_values(transactions):
        """Take a list of transactions and returns a list of cell values."""
        values = []  # [["Date", "", "", "Amount", "", "", "Description"]]

        for trans in transactions:
            medium = get_medium(trans[1])
            values.append(
                [
                    trans[0],
                    "",
                    "",
                    trans[2],
                    "",
                    "",
                    trans[1],
                    "",
                    "",
                    medium,
                    "Yes" if "paypal" in trans[1].lower() else "No",
                    "Yes",
                ]
            )
        return values

    index_last = index + len(transactions) - 1
    range_name = f"Sheet1!A{index + 6}:L{index_last + 6}"

    write_cells(range_name, format_values(transactions))
