"""Read checking information from a txt."""
import calendar

FILE = "account.txt"


def process_data():
    """Read the file and organize data into a list."""
    data = []
    with open(FILE) as account:
        tab_split_data = account.read().split("\t")
        for datum in tab_split_data:
            data.extend(datum.split("\n"))

        data = filter(bool, map(lambda x: x.strip(), data))
        data = tuple(data)
    return data


def group_transactions(data):
    """Convert tuple of data into a list of lists representing transactions."""

    previous_int = False

    def is_float(datum):
        """Determine whether a datum is a float."""
        try:
            float(datum.replace(",", ""))
            return True
        except ValueError:
            return False

    def date_format(date):
        """Convert a date with month abbreviation into a numerical date."""
        date_parts = date.split(" ")
        month_abbr = date_parts[0]
        day = date_parts[1].strip(",")
        year = date_parts[2]
        month_num = list(calendar.month_abbr).index(month_abbr)
        return f"{month_num}/{day}/{year}"

    def is_balance(datum):
        """Determine whether a datum represents a the balance.

        If previous datum was an int and this datum is an int, 
        the datum represents the balance.
        """
        nonlocal previous_int

        balance = previous_int and is_float(datum)
        previous_int = is_float(datum)
        return balance

    transactions = []
    step = 0

    for datum in data:
        formatted_datum = datum
        if step == 0:
            if not transactions or transactions[-1]:
                # Make sure previous is not already blank
                transactions.append([])
            if not is_float(datum):
                # Balances are also processed as step 0; Only format dates
                formatted_datum = date_format(datum)

        if is_balance(formatted_datum):
            transactions[-2].append(formatted_datum)
            step -= 1
        else:
            transactions[-1].append(formatted_datum)

        step += 1
        step %= 3

    return transactions[::-1]


def get_transactions():
    """Process the data and return the transactions."""
    data = process_data()
    return group_transactions(data)
