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


