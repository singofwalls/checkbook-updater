"""Handle interaction with bank website."""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException,
                                        UnexpectedAlertPresentException,
                                        ElementNotVisibleException,
                                        TimeoutException)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from formatting import format_value
import sheet

import time
import json

BANK_INFO = "bank_info.json"
DATE_FORMAT = "%b %d, %Y"

HEADLESS = True


def _expand_table(driver):
    """Expand the transaction table to its full extent."""
    # Load all transactions

    # Select the more transactions button
    try:
        more = driver.find_element_by_css_selector(
            "#table--transactions > tfoot > tr:nth-child(1) > td > button")
        while True:
            # Load all transactions
            time.sleep(1)
            more.click()
    except (ElementNotInteractableException, ElementNotVisibleException):
        # No more transactions
        pass
    time.sleep(1)

    # Double check to ensure no more transactions
    lines = _get_table_lines(driver)
    if "MORE TRANSACTIONS" in lines:
        _expand_table(driver)


def _get_groups(values):
    """Group values into discrete transactions.

    Every 3 values is a single transaction. Group them and yield the groups.
    """

    group = []
    for value in values:
        group.append(value)
        if len(group) == 3:
            yield group
            group = []
    if group:
        yield group


def _parse_entries(raw_lines):
    """Parse the table pulled from the bank into transactions."""

    # First two lines are field names
    entries = []

    for group in _get_groups(raw_lines):
        # Refactor date lines onto start of following line and split tabs
        entry = {}
        first_values = group[0].split(" ")
        entry["Transaction Status"] = " ".join(first_values[:2])
        entry["Date"] = " ".join(first_values[2:])

        entry["Description"] = group[1]
        if " " in group[2]:
            entry["Amount"], entry["Balance"] = group[2].split(" ")
        else:
            # No balance
            entry["Amount"], entry["Balance"] = group[2], ""

        for field in entry:
            entry[field] = format_value(entry[field], field, DATE_FORMAT)

        entries.append(entry)

    return entries


def _get_table_lines(driver):
    """Pull text from table."""
    elem = driver.find_element_by_id("table--transactions")
    text = elem.text.replace("\\n", "\n")
    raw_lines = text.split("\n")[2:]
    return raw_lines


def _process_accounts(driver, accounts):
    """Get entries from every account."""

    entries_list = []

    for i in range(len(accounts)):
        account = accounts[i]

        wait = WebDriverWait(driver, 10)
        account_link = wait.until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, account)))

        account_link.click()
        available = format_value(driver.find_element_by_class_name("h2").text)
        sheet.add_bank_balance(available, account, accounts)

        _expand_table(driver)

        # Get table text
        lines = _get_table_lines(driver)
        entries = _parse_entries(lines)
        # Add account field
        for num in range(len(entries)):
            entries[num]["account"] = account

        entries_list.extend(entries)

        driver.back()

    return entries_list


def _security_question(driver, info):
    """Pass the security question.

    May not be necessary if device already remembered.
    """
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.ID, "horiz-3-question")))
        form = driver.find_element_by_id("securityChallengeForm")
    except (NoSuchElementException, TimeoutException):
        # Not on security page
        return

    question = form.text.split("\n")[0]

    answers = info["security"]
    answer = answers[question]

    input_box = driver.find_element_by_id("securityQuestion")
    input_box.send_keys(answer)

    # Don't ask again checkbox
    box = driver.find_element_by_id("horiz-3-question")
    box.click()

    # Submit
    input_box.send_keys(Keys.RETURN)


def _login(driver, info):
    """Login to my bank account."""
    # Login
    elem = driver.find_element_by_name("username")
    elem.clear()
    elem.send_keys(info["username"])

    elem = driver.find_element_by_name("password")
    elem.clear()
    elem.send_keys(info["password"])
    elem.send_keys(Keys.RETURN)


def _get_driver(info, headless=True):
    """Start a headless webdriver."""
    options = webdriver.ChromeOptions()
    options.headless = headless
    options.add_argument("log-level=3")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options=options)
    driver.get(info["url"])
    return driver


def _get_bank_info():
    """Load the bank info from the json."""
    with open(BANK_INFO) as file:
        return json.load(file)


def get_entries(accounts):
    """Pull transactions from bank website and handle alerts."""

    def _get_entries(accounts, driver, info):
        """Go through the steps of getting transactions from bank website."""
        _login(driver, info)
        _security_question(driver, info)
        entries = _process_accounts(driver, accounts)
        return entries

    info = _get_bank_info()
    driver = _get_driver(info, HEADLESS)
    try:
        return _get_entries(accounts, driver, info)
    except UnexpectedAlertPresentException:
        # Try one more time if an alert appears.
        # Appears to happen after answering security questions which should
        # only be
        # necessary once anyway.
        return _get_entries(accounts, driver, info)
    finally:
        driver.close()
        driver.quit()
