import csv
import logging
import time

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(
    filename='scraping_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def scrape_amazon_static(url: str, output_file: str) -> None:
    """
    Scrapes a given Amazon search page using Requests + BeautifulSoup (static).
    Saves product data (name, price, rating) to a CSV file.

    :param url: The Amazon search URL to scrape.
    :param output_file: The name of the CSV file where results are saved.
    """
    # Set custom headers to appear as a "real" browser
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        ),
        "Accept-Language": "en-US, en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise HTTPError if status != 200
    except Exception as e:
        logging.error(f"Requests error: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Open CSV in write mode
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Price", "Rating"])  # CSV header

        # Find product containers
        products = soup.find_all("div", {"data-component-type": "s-search-result"})
        for product in products:
            try:
                # Extract product name
                name_elem = product.find("h2")
                name = name_elem.get_text(strip=True) if name_elem else "N/A"

                # Extract price
                price_elem = product.find("span", {"class": "a-price-whole"})
                price = price_elem.get_text(strip=True) if price_elem else "N/A"

                # Extract rating
                rating_elem = product.find("span", {"class": "a-icon-alt"})
                rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"

                writer.writerow([name, price, rating])
            except Exception as e:
                logging.error(f"Error parsing product: {e}")

    logging.info(f"Static scrape completed. Data saved to: {output_file}")


def scrape_amazon_dynamic(url: str, output_file: str, headless: bool = True) -> None:
    """
    Scrapes a given Amazon search page using Selenium (dynamic).
    Saves product data (name, price, rating) to a CSV file.
    This approach can handle JavaScript rendering (e.g., infinite scroll).

    :param url: The Amazon search URL to scrape.
    :param output_file: The name of the CSV file where results are saved.
    :param headless: Whether to run Chrome in headless mode (no browser window).
    """
    # Chrome Options for Selenium
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    # (Optional) Reduce debug logging
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    try:
        # Install/update ChromeDriver automatically
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver.get(url)
    except Exception as e:
        logging.error(f"Selenium error: {e}")
        return

    # Use explicit wait to ensure product containers are loaded
    wait = WebDriverWait(driver, 15)  # wait up to 15 seconds
    try:
        wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-component-type='s-search-result']")))
    except Exception as e:
        logging.error(f"Timeout waiting for search results: {e}")
        driver.quit()
        return

    # (Optional) Scroll to the bottom to force lazy-load of additional products
    # This can help if Amazon loads more products dynamically as you scroll.
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # short pause after scrolling

    # Grab all product elements
    products = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")

    # Open CSV in write mode
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Price", "Rating"])

        for product in products:
            try:
                # Extract product name
                name_elem = product.find_element(By.XPATH, ".//h2//span")
                name = name_elem.text.strip() if name_elem else "N/A"

                # Extract price (whole)
                price_elem = product.find_elements(By.XPATH, ".//span[@class='a-price-whole']")
                if price_elem:
                    price = price_elem[0].text.strip()
                else:
                    price = "N/A"

                # Extract rating
                rating_elem = product.find_elements(By.XPATH, ".//span[@class='a-icon-alt']")
                if rating_elem:
                    rating = rating_elem[0].text.strip()
                else:
                    rating = "N/A"

                writer.writerow([name, price, rating])
            except Exception as e:
                logging.error(f"Error parsing product element: {e}")

    driver.quit()
    logging.info(f"Dynamic scrape completed. Data saved to: {output_file}")


if __name__ == "__main__":
    # Example usage: Searching for "laptop" on Amazon India
    amazon_url = "https://www.amazon.in/s?k=laptop"

    # 1. Static scraping example 
    # (May miss data if Amazon heavily uses JS or lazy loads certain elements)
    scrape_amazon_static(amazon_url, "amazon_static.csv")

    # 2. Dynamic scraping example 
    # (Handles JS-rendered elements and typically gets more complete data)
    scrape_amazon_dynamic(amazon_url, "amazon_dynamic.csv", headless=True)
