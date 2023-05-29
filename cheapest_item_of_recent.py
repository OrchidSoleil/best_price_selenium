# This script looks up specific item at the url address, it was given, which has
# the item sorted by recent price (&SortBy=LastSeen&Order=desc). It does so with
# the set frequency and doesn't stop until user stops it manually.
# User personally sets up a threshold price, and the script will notify user if the
# price is below the threshold price.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
import time
from plyer import notification

# Define the URL of the page to scrape
url = ""

# Define the frequency of checking the page (in seconds)
frequency = 600  # check every this amount of seconds
# Define the threshold price in gold below which you want to be notified
threshold_price = 406000

# Set up the Chrome driver with the appropriate options
options = ChromeOptions()
options.add_argument("--headless")
service = ChromeService(executable_path="path/to/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

while True:
    # Load the URL in the driver
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)

    # Find the element that contains the lowest price
    price_elements = driver.find_elements(By.XPATH, "//div[contains(@data-bind, 'Name')] | //span[@data-bind='localizedNumber: UnitPrice'] | //div[contains(@data-bind, 'TraderLocation')] | //div[@data-bind='text: GuildName']")

    # Check if the element exists
    if len(price_elements) > 0:
        lst = [e.text for e in price_elements]
        # convert price to int and remove commas
        dic2 = {int(lst[i].replace(",", "")): lst[i-2] + ', ' + lst[i-1] + ', ' + lst[i-3] for i in range(3, len(lst), 4)}

        lowest_price = min(dic2.keys())
        lowest_location = dic2[lowest_price]

        # Check if the lowest price is below the threshold price
        if lowest_price < threshold_price:

            print(f"{lowest_location} for {lowest_price}!")
            # Display a popup notification in cmd
            notification.notify(
                title="Lowest Price Alert",
                message=f"{lowest_location} for {lowest_price}!",
                timeout=30,
            )
            # Stop the driver

            driver.quit()
        else:
            print(f"The current price is {lowest_price:,} at {lowest_location}. Wait for a better deal.")
    else:
        print("Could not find lowest price element.")

    # Pause the execution of the script for the specified frequency
    time.sleep(frequency)
