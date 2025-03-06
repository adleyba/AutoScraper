# AutoScraper

📊 **AutoScraper** – A Python-based web scraper that extracts car listings, prices, and essential details from [MyAuto.ge](https://www.myauto.ge). This script utilizes **Selenium**, **BeautifulSoup**, and **CloudScraper** to efficiently collect data and save it into an Excel file.

⚠️ **This project is for educational purposes only.**  
🚫 **Commercial use is strictly prohibited.**

## Features 🚀
- **Extracts car data** (name, price, mileage, license number, production year, etc.)
- **Saves results to an Excel file**
- **Uses Selenium to interact with the website**
- **Bypasses Cloudflare protection** with CloudScraper
- **Handles pagination dynamically**
- **User input allows specifying the number of pages to scrape**

## Installation 🛠️

### Prerequisites:
- Python 3.x
- Google Chrome & ChromeDriver (matching versions)

### Install required dependencies:
```sh
pip install -r requirements.txt
```

### Setup ChromeDriver:
Download **ChromeDriver** matching your Chrome version from [here](https://chromedriver.chromium.org/downloads) and place it in the project directory.

## Usage 📖
Run the script with:
```sh
python full_parse.py
```

The script will ask for a **MyAuto.ge URL** and the number of pages to scrape. If left empty, it scrapes all available pages.

### Example Run:
```
Enter URL to scrape: https://www.myauto.ge/en/s/for-sell-cars-mercedes-benz?vehicleType=0&bargainType=0&mansNModels=25&currId=3&mileageType=1&layoutId=1)
How many pages would you like to parse? Press Enter if you want to parse all pages: 5
```

The extracted data will be saved in an Excel file named like:
```
12.03.2025_14_30_car_data.xlsx
```

## How It Works 🔍
1. **Opens the given MyAuto.ge URL** using Selenium.
2. **Intercepts API calls** to find the backend data source.
3. **Extracts metadata** to determine the total number of pages.
4. **Loops through the pages**, extracting car details.
5. **Stores the data in an Excel file**, appending new results.

## Technologies Used 🛠️
- **[Selenium](https://www.selenium.dev/documentation/webdriver/)** – For automated browsing
- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)** – For parsing HTML
- **[CloudScraper](https://pypi.org/project/cloudscraper/)** – To bypass Cloudflare protection
- **Pandas & OpenPyXL** – For handling and saving data in Excel format

## Disclaimer ⚠️
This project is strictly for **educational and research purposes**. **Scraping websites without permission may violate their terms of service.** Please ensure compliance with [MyAuto.ge's terms](https://www.myauto.ge/) before running this script.

## License 📜
**Apache license 2.0**

---
Made with ❤️ for educational purposes.
