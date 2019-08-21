"""Read new transactions and update master sheet."""

import new_data as new
import old_data as old

from sheets import authorize


def find_transaction(transaction, transactions):
    """Find the index of a transaction in a list of transactions.
    
    Notes
    -----
    A transaction list holds the following values:
        0: date
        1: description
        2: amount
        3: balance (OPTIONAL)

    """
    def format_money(money):
        return float(money.replace("$", "").replace(",", ""))

    # Check amounts
    amount_matches = [
        trans
        for trans in transactions
        if format_money(trans[2]) == format_money(transaction[2])
    ]
    if not amount_matches:
        # No amounts match, go back to checking all transactions
        amount_matches = transactions

    if len(amount_matches) == 1:
        return transactions.index(amount_matches[0])

    # Check descriptions
    description_matches = [
        trans for trans in amount_matches if trans[1].lower() == transaction[1].lower()
    ]
    if not description_matches:
        # No descriptions match, go back to checking amount matches
        description_matches = amount_matches

    if len(description_matches) == 1:
        return transactions.index(description_matches[0])

    # Check dates
    date_matches = [
        trans for trans in description_matches if trans[0] == transaction[0]
    ]
    if not date_matches:
        # No dates match, go back to checking description matches
        date_matches = description_matches

    if len(date_matches) == 1:
        return transactions.index(date_matches[0])

    # Check balances
    balance_matches = [
        trans
        for trans in date_matches
        if len(trans) >= 4 and format_money(trans[3]) == format_money(transaction[3])
    ]
    if len(balance_matches) != 1:
        # Either suddenly no matches found at this stage, or multiple matches still remain
        breakpoint()
        raise Exception("Multiple matches for last transaction on sheet in bank list.")
    else:
        return transactions.index(balance_matches[0])


def main():
    """Start the script."""
    authorize()

    transactions_new = new.get_transactions()
    transactions_old = old.get_transactions()

    # Find the new transactions not already in old
    last_transaction = transactions_old[-1]
    index_last_new = find_transaction(last_transaction, transactions_new)
    transactions_unrecorded = transactions_new[index_last_new + 1 :]

    index_last_old = len(transactions_old)

    old.add_transactions(transactions_unrecorded, index_last_old)


if __name__ == "__main__":
    main()
