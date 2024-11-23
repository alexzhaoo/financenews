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

# Function to scrape search results data
def scrape_cnbc_search_results(query):
    # Set up WebDriver options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--ignore-certificate-errors")
    
    # Start the WebDriver
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Open the CNBC search results page
    search_url = f'https://www.cnbc.com/search/?query={query}&qsearchterm={query}'
    driver.get(search_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'SearchResult-searchResultTitle')))  # Explicit wait
    
    # Comment out or remove the page source print statement
    # print(driver.page_source)
    articles = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    # Find the search result items
    try:

        while len(articles) < 20:

            # Scroll down to the bottom of the page and load articles
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")     
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'SearchResult-searchResultTitle')))

            # Loop through each search result item to extract the title and link
            search_result_items = driver.find_elements(By.CLASS_NAME, 'SearchResult-searchResultTitle')
            for item in search_result_items:
                try:
                    # Extract title and link
                    link_element = item.find_element(By.CLASS_NAME, 'resultlink')

                    title = link_element.text.strip()
                    link = link_element.get_attribute('href')

                    # Append the data
                    if title and link:
                        articles.append({'title': title, 'link': link})

                        # Debug log
                        print(f"Title: {title}\nLink: {link}\n")
                    
                except Exception as e:
                    print(f"Error extracting article: {e}")

        # Close the driver after scraping
        driver.quit()

        # Write articles to CSV
        if articles:
            write_to_csv(articles, f'CNBCSearchResults_{query}.csv')
        else:
            print("No articles found.")
    
    except Exception as e:
        print(f"Error finding the search results: {e}")
        driver.quit()

# Function to write the scraped data to a CSV file
def write_to_csv(data, file_name='CNBCHomepageNews.csv'):
    print(f"Writing {len(data)} articles to {file_name}...")
    
    keys = data[0].keys()
    with open(file_name, 'w', encoding='utf-8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

    print('Data successfully written to CSV!')

#scrape_cnbc_homepage()
scrape_cnbc_search_results('stocks')