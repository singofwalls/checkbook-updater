from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotInteractableException
from bs4 import BeautifulSoup

import bank

import time
import json
import os


BANK_INFO = "bank_info.json"


def _expand_table(driver):
    """Expand the transaction table to its full extent."""
    # Load all transactions

    # Select the more transactions button
    try:
        more = driver.find_element_by_css_selector(
            "#table--transactions > tfoot > tr:nth-child(1) > td > button"
        )
        while True:
            # Load all transactions
            time.sleep(1)
            more.click()
    except ElementNotInteractableException:
        # No more transactions
        pass
    time.sleep(1)


def _save_transactions(text, account):
    """Save the transactions to a text document."""
    if not os.getcwd().strip("\\").endswith(bank.FILE_PATH.strip("/")):
        os.chdir(bank.FILE_PATH)

    file_name = f"{account}.txt"
    try:
        os.remove(file_name)
    except FileNotFoundError:
        pass
    with open(file_name, "w") as file:
        file.write(text)


def _process_accounts(driver, accounts):
    """Go to each account page."""

    for i in range(3):
        while True:
            try:
                account_links = driver.find_elements_by_class_name("slat__clickable")
                account_links[i].click()
                break
            except Exception:
                time.sleep(1)
        _expand_table(driver)

        # Get table text
        elem = driver.find_element_by_id("table--transactions")
        text = elem.text.replace("\\n", "\n")
        _save_transactions(text, accounts[i])

        driver.back()


def _security_question(driver, info):
    """Pass the security question.

    May not be necessary if device already remembered.
    """
    # TODO: Automatically determine if on sec page
    input_box = driver.find_element_by_id("securityQuestion")
    input_box.send_keys(info["security"])

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


def _get_driver(info):
    """Start a headless webdriver."""
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get(info["url"])
    return driver


def _get_bank_info():
    """Load the bank info from the json."""
    with open(BANK_INFO) as file:
        return json.load(file)


def get_entries(accounts):
    """Pull transactions from bank website."""

    info = _get_bank_info()
    driver = _get_driver(info)
    _login(driver, info)
    _process_accounts(driver, accounts)


if __name__ == "__main__":
    get_entries(["Savings", "Checking", "School"])
