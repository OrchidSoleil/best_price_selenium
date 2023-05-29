# This script searches for a specific item on the [...] website,
# then checks the lowest margin of suggested price and returns a list of items below that margin.
# Then sends notification to the user if the price is below the lowest margin of suggested price.

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
from plyer import notification


# set up logger debugger
logging.basicConfig(filename='log.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


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
    search_box.send_keys("Columbine")
    search_box.send_keys(Keys.RETURN)
    # switch to the new tab
    driver.switch_to.window(driver.window_handles[1])
    lst = []
    item = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@data-bind, 'Name')]")))
    item.click()
    driver.switch_to.window(driver.window_handles[2])
    suggested_price_low = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[@data-bind='localizedNumber:SuggestedPrice']"))).text
    print(f"Suggested price is {suggested_price_low}")
    # close this tab
    driver.close()
    # return to a previous tab
    driver.switch_to.window(driver.window_handles[1])
    # from the next 2 pages get the elements and append them to a list
    for i in range(3):
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
    with open('below_average.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        # create headers in a csv file
        writer.writerow(['Item', 'Location', 'Guild', 'Price', 'Last Seen', 'Time Frame'])
        # write the nested list to the csv file
        for price in deals:
            # turn prices to floats and compare
            if float(price[3]) < float(suggested_price_low.replace(',', '')):
                writer.writerows([price])
            else:
                pass
    driver.quit()
    return 'below_average.csv'


# scan_prices(url)


def notify(your_csv):
    with open(your_csv, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        # check if there's any data in the csv file with if any()
        if any(row for row in reader):
            f.seek(0)  # return to the beginning of the file
            next(reader)  # skip header again
            # sort the csv file by price
            reader = sorted(reader, key=lambda row: float(row[3]))
            low_price = reader[0]  # define the first row as the lowest price
            print(f"{low_price[0]} for {int(low_price[3]):,} in {low_price[1]} at {low_price[2]} last seen {low_price[4]} {low_price[5]} ago.")
            # send notification to UI
            notification.notify(
                title='A great deal!',
                message=f"{low_price[0]} for {int(low_price[3]):,} in {low_price[1]} at {low_price[2]} last seen {low_price[4]} {low_price[5]} ago.",
                timeout=60
            )
            print('Other options:')
            for row in reader:
                print(row)
        else:
            print("No deals found. Try again later.")


notify(scan_prices(url))
# notify('below_average.csv')
