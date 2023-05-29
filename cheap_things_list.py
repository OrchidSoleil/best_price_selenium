# This script searches for a specific item on the {...} website and returns a list of the cheapest deals sorted by price.

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# set up logger debugger
logging.basicConfig(filename='log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Set up the Chrome driver with the appropriate options
options = ChromeOptions()
# options.add_argument("--headless")
service = ChromeService(executable_path="path/to/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

url = ""


def scan_prices(your_url):
    driver.get(your_url)
    wait = WebDriverWait(driver, 10)
    # search_box = wait.until(EC.element_to_be_clickable((By.ID, "search-form")))
    search_box = wait.until(EC.visibility_of_element_located((By.XPATH, "//form[@id='search-form']//input[@type='text']")))
    search_box.clear()
    search_box.send_keys("Invisibility Potion")
    search_box.send_keys(Keys.RETURN)
    # switch to the new tab
    driver.switch_to.window(driver.window_handles[1])
    lst = []
    # from the next 2 pages get the elements and append them to a list
    for i in range(4):
        price_elements = driver.find_elements(By.XPATH, "//div[contains(@data-bind, 'Name')] | //span[@data-bind='localizedNumber: UnitPrice'] | //div[contains(@data-bind, 'TraderLocation')] | //div[@data-bind='text: GuildName'] | //td[contains(@data-bind, 'minutesElapsed')]")
        for element in price_elements:
            lst.append(element.text)
        # move to the next page up to three times if there are more pages
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@data-bind, 'Name')]")))
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            next_page = driver.find_element(By.CSS_SELECTOR, "#search-result-view > div:nth-child(1) > div > div > ul > li:nth-child(14) > a")
            next_page.click()
            time.sleep(5)
        except NoSuchElementException or TimeoutException:
            print("Element not found")
            break
    # make a list of nested lists and write it to a csv file
    deals = [lst[i:i+5] for i in range(0, len(lst), 5)]
    for deal in deals:
        last_seen_separate_digit = deal[-1].split(' ')
        deal[-1:] = last_seen_separate_digit
        remove_comma_in_price = deal[3].replace(',', '')
        deal[3] = remove_comma_in_price
    with open('cheap_things.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        # create headers in a csv file
        writer.writerow(['Item', 'Location', 'Guild', 'Price', 'Last Seen', 'Time Frame'])
        # write the nested list to the csv file
        writer.writerows(deals)
    return 'cheap_things.csv'


def view_the_prices(csv_file):
    # sort the csv file by price
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        # skip the header
        next(reader)
        # f.seek(0)  # reset the file pointer to the beginning if reader was once exhausted
        # convert the price to float and sort the list by price
        sort_by_price = sorted(reader, key=lambda row: float(row[3]), reverse=False)
        # first row is the best price
        print(sort_by_price[0])
        print('Other options:')
        for option in sort_by_price[1:]:
            print(option)


# view_the_prices('cheap_things.csv')
view_the_prices(scan_prices(url))
