import cloudscraper
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import json
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

# Paths for Chrome and WebDriver
custom_chrome_path = "chrome-win64/chrome.exe"
custom_driver_path = "chromedriver.exe"

# Set up Chrome options for Selenium
chrome_options = Options()
chrome_options.binary_location = custom_chrome_path
chrome_options.add_argument("--window-size=100,100")
chrome_options.add_argument("--log-level=3")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
chrome_options.add_argument("--disable-sync")
chrome_options.add_argument("--disable-background-networking")
chrome_options.add_argument("--disable-default-apps")
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

# Start Chrome WebDriver
service = Service(custom_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Request URL from the user
url = input("Enter URL to scrape: ").strip()
if not url:
    print("Error: URL cannot be empty.")
    driver.quit()
    exit()

# Remove 'page' parameter from the URL to avoid conflicts
parsed_url = urlparse(url)
query_params = parse_qs(parsed_url.query)
query_params.pop("page", None)
new_query = urlencode(query_params, doseq=True)
url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query, parsed_url.fragment))

# Open the first page in the browser
driver.get(f"{url}&page=1")

# Wait for the page to load
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "line-clamp-1"))
    )
except Exception as e:
    print(f"Error: Page did not load properly. {e}")
    driver.quit()
    exit()

# Extract network logs to find API Gateway
logs = driver.get_log("performance")
gateway = ""

for log in logs:
    try:
        message = json.loads(log["message"])["message"]
        if message["method"] == "Network.requestWillBeSent":
            request_url = message["params"]["request"]["url"]
            if request_url.startswith("https://api2.myauto.ge/en/products?"):
                gateway = request_url
                print("Found API Gateway:", request_url)
                break
    except Exception:
        continue

if not gateway:
    print("Error: API Gateway not found.")
    driver.quit()
    exit()

# Remove 'page' parameter from API Gateway URL
parsed_url = urlparse(gateway)
query_params = parse_qs(parsed_url.query)
query_params.pop("Page", None)
new_query = urlencode(query_params, doseq=True)
gateway = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query, parsed_url.fragment))

# Request metadata to determine the total number of pages
scraper = cloudscraper.create_scraper()
response = scraper.get(gateway)
meta = response.json().get("data", {}).get("meta", {})
last_page = meta.get("last_page", 1)
print(f"Total pages: {last_page}")

# Generate timestamped filename
timestamp = datetime.now().strftime("%d.%m.%Y_%H_%M")
excel_filename = f"{timestamp}_car_data.xlsx"

# Ask the user for the number of pages to scrape
pages_to_parse = input("How many pages would you like to parse? Press Enter to parse all pages: ").strip()
try:
    range_to_parse = range(1, last_page + 1) if not pages_to_parse else range(1, int(pages_to_parse) + 1)
except ValueError:
    print("Error: Invalid input. Please enter a valid number.")
    driver.quit()
    exit()

# Iterate over pages and scrape data
for i in range_to_parse:
    page_url = f"{url}&page={i}&sort=1"
    print(f"Parsing page: {page_url}")
    driver.get(page_url)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "line-clamp-1"))
        )
    except Exception as e:
        print(f"Error: Failed to load page {i}. {e}")
        continue
    
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    links = soup.find_all("a", class_="line-clamp-1 text-raisin-100")
    texts = [link.get_text(strip=True) for link in links]
    
    response = scraper.get(f"{gateway}&SortOrder=1&Page={i}")
    items = response.json().get("data", {}).get("items", [])
    
    cars = []
    for d, car in enumerate(items):
        if d >= len(texts):
            break

        link = f"https://www.myauto.ge/en/pr/{car['car_id']}"
        price = car.get("price")
        if price:
            car_dict = {
                "car name": texts[d],
                "client_name": car.get("client_name", "Unknown"),
                "url": link,
                "price(usd)": price,
                "car mileage(km)": car.get("car_run_km", 0),
                "license_number(if exists)": car.get("license_number", ""),
                "production year": car.get("prod_year", 0),
            }
            cars.append(car_dict)
    
    df = pd.DataFrame(cars)
    if os.path.exists(excel_filename):
        existing_df = pd.read_excel(excel_filename)
        df = pd.concat([existing_df, df], ignore_index=True)
    df.to_excel(excel_filename, index=False)
    print(f"Saved {len(cars)} records to {excel_filename}")

# Close WebDriver
driver.quit()
