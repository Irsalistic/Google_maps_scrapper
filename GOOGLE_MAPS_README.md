# Google Maps Business Scraper

This Python script automates the process of scraping business information from Google Maps using Selenium and additional tools. It extracts data such as business name, address, phone number, website, LinkedIn page, reviews, and email addresses.

---

## Features

- Scrapes data for specific business types in a given location.
- Saves the extracted data to a CSV file.
- Uses multiprocessing for faster data scraping.
- Extracts emails from business websites and finds LinkedIn pages.
- Scrolls and fetches multiple pages of results from Google Maps.

---

## Prerequisites

Before running the script, ensure the following are installed:

1. **Python**: Install Python version 3.9 or higher.
2. **Google Chrome**: Ensure Google Chrome is installed on your system.
3. **ChromeDriver**: Managed and installed automatically by `webdriver-manager`.

---

## Installation

### Step 1: Clone or Download the Repository

Clone this repository or download the ZIP file and extract it.

### Step 2: Install Dependencies

Install the required Python libraries using the following command:

```bash
pip install -r requirements.txt
```

```bash
python maps_scraper.py --business_type "business type" --location "location"
```