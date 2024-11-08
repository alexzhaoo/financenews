from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv
import time
import os
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables
load_dotenv()

CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')

# Function to scrape homepage data
def scrape_cnbc_homepage():
    # Set up WebDriver options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run headless if you prefer
    chrome_options.add_argument("--ignore-certificate-errors")
    
    # Start the WebDriver
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Open the CNBC homepage
    driver.get('https://www.cnbc.com')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'LatestNews-item')))  # Explicit wait
    
    # Print page source for debugging
    print(driver.page_source)
    
    # Find the 'LatestNews-list' section
    try:
        latest_news_items = driver.find_elements(By.CLASS_NAME, 'LatestNews-item')  # Verify this class name

        # Loop through each 'LatestNews-item' to extract the title and link
        articles = []
        for item in latest_news_items:
            try:
                # Extract title and link
                title_element = item.find_element(By.TAG_NAME, 'a')
                title = title_element.text
                link = title_element.get_attribute('href')

                # Store in a dictionary
                articles.append({
                    'title': title,
                    'link': link
                })

                print(f"Title: {title}\nLink: {link}\n")

            except Exception as e:
                print(f"Error extracting article: {e}")

        # Close the driver after scraping
        driver.quit()

        # Write articles to CSV
        if articles:
            write_to_csv(articles)
        else:
            print("No articles found.")
    
    except Exception as e:
        print(f"Error finding the LatestNews list: {e}")
        driver.quit()

# Function to scrape search results from CNBC
def scrape_cnbc_search(search_term):
    # Set up WebDriver options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run headless if you prefer
    chrome_options.add_argument("--ignore-certificate-errors")
    
    # Start the WebDriver
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Open the CNBC search page with the search term
    search_url = f'https://www.cnbc.com/search/?query={search_term}&qsearchterm={search_term}'
    driver.get(search_url)

    # Use WebDriverWait to wait for search results to load
    # Find the search results section
    try:
        # Using partial class name "SearchResult-searchResult" to find each search result
        search_results = driver.find_elements(By.CLASS_NAME, 'SearchResult-searchResult')

        # Loop through each search result to extract the title and link
        articles = []
        for result in search_results:
            try:
                # Extract title and link from within the result item
                title_element = result.find_element(By.CLASS_NAME, 'SearchResult-searchResult')  # Finding the title within the item
                title = title_element.text
                link_element = result.find_element(By.TAG_NAME, 'a')   # Finding the link within the item
                link = link_element.get_attribute('href')

                # Store in a dictionary
                articles.append({
                    'title': title,
                    'link': link
                })

                print(f"Title: {title}\nLink: {link}\n")

            except Exception as e:
                print(f"Error extracting article: {e}")

        # Close the driver after scraping
        driver.quit()

        # Write articles to CSV
        if articles:
            write_to_csv(articles)
        else:
            print("No articles found.")
        
    except Exception as e:
        print(f"Error finding the search results: {e}")
        driver.quit()

# Function to write the scraped data to a CSV file
def write_to_csv(data):
    file_name = 'CNBCHomepageNews.csv'
    print(f"Writing {len(data)} articles to {file_name}...")
    
    keys = data[0].keys()
    with open(file_name, 'w', encoding='utf-8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

    print('Data successfully written to CSV!')

# Run the scraper with the search term "tech"
#scrape_cnbc_homepage()
scrape_cnbc_search('stocks')
