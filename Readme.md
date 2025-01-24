# Amazon Product Scraper

This project provides two methods to scrape Amazon product data—**Name**, **Price**, and **Rating**—from a search results page:

1. **Static Scraper** using [Requests](https://pypi.org/project/requests/) + [BeautifulSoup](https://pypi.org/project/beautifulsoup4/).
2. **Dynamic Scraper** using [Selenium](https://pypi.org/project/selenium/) + [ChromeDriver](https://sites.google.com/chromium.org/driver/) (managed by [webdriver-manager](https://pypi.org/project/webdriver-manager/)).

Both scrapers store the extracted data in CSV files for easy analysis.

---

## Features

- **Amazon Search**: Scrape listings from any Amazon search URL.
- **Extracted Fields**: Product **Name**, **Price**, and **Rating**.
- **Static Scraper (Requests + BS4)**: Faster but may miss dynamic (JS-loaded) data.
- **Dynamic Scraper (Selenium)**: Uses a real browser to handle JavaScript, ensuring more complete data capture.
- **CSV Output**: Outputs data to `amazon_static.csv` and `amazon_dynamic.csv`.
- **Logging**: Records info and errors in `scraping_log.log`.

---

## Requirements

- **Python 3.7+**
- **pip** (or `pipenv`, `conda`, etc.) to install dependencies

---
