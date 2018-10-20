"""Read new transactions and update master sheet."""

import read_new_data as new
import read_old_data as old

from sheets import authorize


def find_transaction(transaction, transactions):
    """Find the index of a transaction in a list of transactions."""

    def format_money(money):
        return float(money.replace("$", "").replace(",", ""))

    # Check prices
    price_matches = [
        trans
        for trans in transactions
        if format_money(trans[2]) == format_money(transaction[2])
    ]
    if not price_matches:
        # No prices match, go back to checking all transactions
        price_matches = transactions

    if len(price_matches) == 1:
        return transactions.index(price_matches[0])

    # Check descriptions
    description_matches = [
        trans for trans in price_matches if trans[1].lower() == transaction[1].lower()
    ]
    if not description_matches:
        # No descriptions match, go back to checking price matches
        description_matches = price_matches

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
    authorize()

    transactions_new = new.get_transactions()
    transactions_old = old.get_transactions()

    last_transaction = transactions_old[-1]
    last_transaction_index = find_transaction(last_transaction, transactions_new)
    transactions_unrecorded = transactions_new[last_transaction_index + 1 :]


if __name__ == "__main__":
    main()
