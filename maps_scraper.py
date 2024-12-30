import csv
import time
import os
import argparse
import random
from multiprocessing import Pool, Manager

import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from emailfinder.extractor import *
from googlesearch import search
import tldextract

from selenium.webdriver.chrome.service import Service


def find_linkedin_page(domain):
    query = f'site:linkedin.com/company {domain}'
    linkedin_url = None

    for result in search(query, num_results=2):
        if "linkedin.com/company" in result:
            linkedin_url = result
            break
        time.sleep(random.uniform(2, 5))

    return linkedin_url




def get_base_domain(url):
    extracted = tldextract.extract(url)
    return f"{extracted.domain}.{extracted.suffix}"


def scrape_business_data(url):
    # Initialize a new Chrome driver instance for each process
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)

    output = {}
    try:
        output['name'] = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'DUwDvf'))
        ).text
    except Exception:
        output['name'] = ""

    try:
        url_xpath = driver.find_element(By.XPATH, "//a[@data-tooltip='Open website']")
        output['url'] = get_base_domain(url_xpath.get_attribute('href'))
    except Exception:
        output['url'] = ""

    try:
        phone_xpath = "//button[contains(@data-item-id, 'phone')]"
        phone_number = driver.find_element(By.XPATH, phone_xpath).text.split()[-2:]
        output['phone'] = " ".join(phone_number)
    except Exception:
        output['phone'] = ""

    try:
        reviews_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[2]/span/span'
        output['reviews'] = driver.find_element(By.XPATH, reviews_xpath).text
    except Exception:
        output['reviews'] = ""

    try:
        address_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div[3]/button/div/div[2]/div[1]'
        output['address'] = driver.find_element(By.XPATH, address_xpath).text
    except Exception:
        output['address'] = ""

    try:
        output['emails'] = get_emails_from_google(output['url'])
    except Exception:
        output['emails'] = ""

    try:
        output['linkedin_page'] = find_linkedin_page(output['url'])
    except Exception:
        output['linkedin_page'] = ""

    driver.quit()
    return (
        output['name'], output['address'], output['phone'], output['url'], output['linkedin_page'], output['reviews'],
        output['emails'])


def main():
    # Create the output folder if it doesn't exist
    if not os.path.exists('output'):
        os.makedirs('output')

    parser = argparse.ArgumentParser(description='Scrape businesses from Google Maps')
    parser.add_argument('--business_type', '-bt', '-business_type', '--bt', type=str, nargs="+")
    parser.add_argument('--location', '-l', '-location', '--l', type=str, nargs="+")
    args = parser.parse_args()

    location = " ".join(args.location)
    business_type = " ".join(args.business_type)

    print(f"Searching for {business_type} in {location}")

    # Initialize Chrome driver for searching businesses
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get('https://www.google.com/maps')

    # Wait for the search box to load and perform the search
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'searchboxinput'))
        )
        search_query = f'{business_type} in {location}'
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)

        # Wait for search results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'hfpxzc'))
        )
    except Exception as e:
        print("Error: Failed to load search results")
        driver.quit()
        return

    # Initialize the list of business URLs
    urls = []
    while True:
        try:
            businesses = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'hfpxzc'))
            )
            for business in businesses:
                url = business.get_attribute('href')
                if url not in urls:
                    urls.append(url)
            driver.execute_script("arguments[0].scrollIntoView();", businesses[-1])
            time.sleep(2)
            new_businesses = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'hfpxzc'))
            )
            if len(new_businesses) == len(businesses):
                break
        except Exception:
            break

    driver.quit()

    # Use multiprocessing to scrape each business URL
    with Manager() as manager:
        with Pool(processes=12) as pool:  # Adjust the number of processes as needed
            output = pool.map(scrape_business_data, urls)

    # Write the output to a CSV file
    csv_filename = f'output/{location}.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Address', 'Phone', "URL", "LinkedIn", "Reviews", "Emails"])
        writer.writerows(output)

    print(f'Successfully scraped {len(output)} businesses.')
    print("Scraping completed.")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"total_time: {end_time - start_time}")



# import csv
# import time
# import os
# import argparse
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# # from emailfinder import EmailFinder
# from emailfinder.extractor import *
# from googlesearch import search
#
# import tldextract
#
# start_time = time.time()
#
#
# def find_linkedin_page(domain):
#     query = f'site:linkedin.com/company {domain}'
#     linkedin_url = None
#
#     # Add a random delay between requests to avoid 429 error
#     for result in search(query, num_results=2):
#         if "linkedin.com/company" in result:
#             linkedin_url = result
#             break
#
#         # Random delay after each request
#         time.sleep(5)
#
#     return linkedin_url
#
#
# def get_base_domain(url):
#     extracted = tldextract.extract(url)
#     # Combine domain and suffix to get the base domain
#     return f"{extracted.domain}.{extracted.suffix}"
#
#
# # Initialize email finder
# # email_finder = EmailFinder()
#
# # Create the output folder if it doesn't exist
# if not os.path.exists('output'):
#     os.makedirs('output')
#
# parser = argparse.ArgumentParser(description='Scrape businesses from Google Maps')
# parser.add_argument('--business_type', '-bt', '-business_type', '--bt', type=str, nargs="+")
# parser.add_argument('--location', '-l', '-location', '--l', type=str, nargs="+")
#
# args = parser.parse_args()
#
# location_args = args.location
# location = " ".join(location_args)
#
# business_type_args = args.business_type
# business_type = " ".join(business_type_args)
#
# print(f"Searching for {business_type} in {location}")
#
# # Initialize Chrome driver
# driver = webdriver.Chrome(ChromeDriverManager().install())
#
# # Open the website
# driver.get('https://www.google.com/maps')
#
# # Wait for the search box to load
# try:
#     search_box = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.ID, 'searchboxinput'))
#     )
#
#     # Type the search query and press Enter
#     search_query = f'{business_type} en {location}'
#     search_box.send_keys(search_query)
#     search_box.send_keys(Keys.RETURN)
#
#     # Wait for the search results to load
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CLASS_NAME, 'hfpxzc'))
#     )
# except:
#     # Retry if an exception occurs
#     time.sleep(5)
#     try:
#         search_box = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, 'searchboxinput'))
#         )
#         search_query = f'{business_type} in {location}'
#         search_box.send_keys(search_query)
#         search_box.send_keys(Keys.RETURN)
#
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, 'hfpxzc'))
#         )
#     except:
#         print("Error: Failed to load search results")
#         driver.quit()
#         exit()
#
# # Initialize the output list
# output = []
# urls = []
#
# while True:
#     try:
#         # Find all the businesses in the search results
#         businesses = WebDriverWait(driver, 10).until(
#             EC.presence_of_all_elements_located((By.CLASS_NAME, 'hfpxzc'))
#         )
#     except:
#         break
#
#     time.sleep(2)
#
#     # Store the URLs of the businesses
#     for business in businesses:
#         url = business.get_attribute('href')
#         if url not in urls:
#             urls.append(url)
#
#     # Scroll down to load more businesses
#     driver.execute_script("arguments[0].scrollIntoView();", businesses[-1])
#     time.sleep(2)
#
#     try:
#         new_businesses = WebDriverWait(driver, 10).until(
#             EC.presence_of_all_elements_located((By.CLASS_NAME, 'hfpxzc'))
#         )
#         if len(new_businesses) == len(businesses):
#             break
#     except:
#         break
#
# # Visit each business URL and scrape the data
# for url in urls:
#     driver.get(url)
#
#     try:
#         name = WebDriverWait(driver, 2).until(
#             EC.presence_of_element_located((By.CLASS_NAME, 'DUwDvf'))
#         ).text
#     except Exception as e:
#         name = ""
#
#     try:
#         # url_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div[6]/a/div/div[2]/div[1]'
#         # url = driver.find_element(By.XPATH,url_xpath).text
#
#         url_xpath = driver.find_element(By.XPATH, "//a[@data-tooltip='Open website']")
#         # url = url_xpath.get_attribute('href').split("/", 3)[:3]
#         # url = "/".join(url).split("//")[1]
#         # url = url.split(".")[-2:]
#         # url = ".".join(url)
#         url = url_xpath.get_attribute('href')
#         url = get_base_domain(url)
#         # url = driver.find_element(By.XPATH,url_xpath).text
#
#         print(f"url: {url}")
#         # emails = get_emails_from_bing(url)
#     except Exception as e:
#         url = ""
#
#     try:
#         phone_xpath = "//button[contains(@data-item-id, 'phone')]"
#         phone_number = driver.find_element(By.XPATH, phone_xpath).text.split()[-2:]
#         phone = " ".join(phone_number)
#
#     except Exception as e:
#         phone = ""
#
#     try:
#         reviews_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/span[2]/span/span'
#         reviews = driver.find_element(By.XPATH, reviews_xpath).text
#     except Exception as e:
#         reviews = ""
#
#     try:
#         address_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div[3]/button/div/div[2]/div[1]'
#         address = driver.find_element(By.XPATH, address_xpath).text
#     except Exception as e:
#         address = ""
#
#     # Use emailfinder to find emails on the business website
#     try:
#         time.sleep(3)
#         emails1 = get_emails_from_google(url)
#         time.sleep(3)
#     except Exception as e:
#         emails1 = ""
#
#     try:
#         # time.sleep(5)
#         linkedin_page = find_linkedin_page(url)
#         # time.sleep(5)
#     except:
#         linkedin_page = ""
#     # Append data to output list
#     print(f"name: {name}")
#     print(f"address: {address}")
#     print(f"phone: {phone}")
#     print(f"url: {url}")
#     print(f"reviews: {reviews}")
#     print(f"emails: {emails1}")
#     print(f"linkedin_page: {linkedin_page}")
#     output.append((name, address, phone, url, linkedin_page, reviews, emails1))
#
# # Close the driver
# driver.quit()
#
# csv_filename = f'output/{location}.csv'
# # Write the output to a CSV file
# with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(['Name', 'Address', 'Phone', "URL", "LinkedIn", "Reviews", "Emails"])
#     writer.writerows(output)
# end_time = time.time()
# total_time = end_time - start_time
# print(f'Successfully scraped {len(output)} businesses.')
# print("Scraping completed.")
# print(f"Total Time: {total_time}")

