from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv
import os
import json
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables
load_dotenv()

CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE_PATH = os.path.join(SCRIPT_DIR, '../cookies.json')  # Path to the cookies file

if not os.path.exists(COOKIES_FILE_PATH):
    print(f"Cookies file not found at {COOKIES_FILE_PATH}")
else:
    print(f"Cookies file found at {COOKIES_FILE_PATH}")

def load_cookies(driver, cookies_file_path):
    with open(cookies_file_path, 'r') as cookies_file:
        cookies = json.load(cookies_file)
        for cookie in cookies:
            # Adjust the cookie domain if necessary
            if 'sameSite' in cookie:
                del cookie['sameSite']
            if 'domain' in cookie:
                cookie['domain'] = '.cnbc.com'
            driver.add_cookie(cookie)

def sign_in(driver):
    try:
        driver.get('https://www.cnbc.com')
        
        # Load cookies
        load_cookies(driver, COOKIES_FILE_PATH)
        
        # Refresh the page to apply cookies
        driver.refresh()

        # Wait for the sign-in process to complete
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ProfileIcon-profileIconContainer'))
        )
        print("Sign-in was successful using cookies.")
        return True
    except TimeoutException:
        print("Sign-in failed or took too long.")
        return False

def scrape_article_bullet_points(driver, article_url):
    driver.get(article_url)
    
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'ArticleBody-articleBody')))

    bullet_points = []
    try:
        groups = driver.find_elements(By.CLASS_NAME, 'group')

        for group in groups:
            ul_elements = group.find_elements(By.TAG_NAME, 'ul')

            for ul in ul_elements:
                li_elements = ul.find_elements(By.TAG_NAME, 'li')

                for li in li_elements:
                    bullet_points.append(li.text.strip())

    except Exception as e:
        print(f"Error extracting bullet points: {e}")

    return bullet_points

# Function to scrape search results data
def scrape_cnbc_search_results(driver, query, max_articles):
    search_url = f'https://www.cnbc.com/search/?query={query}&qsearchterm={query}'
    driver.get(search_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'SearchResult-searchResultTitle')))

    articles = []
    seen_articles = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    try:
        while len(articles) < max_articles:
            search_result_items = driver.find_elements(By.CLASS_NAME, 'SearchResult-searchResultTitle')
            
            for item in search_result_items:
                try:
                    link_element = item.find_element(By.CLASS_NAME, 'resultlink')

                    title = link_element.text.strip()
                    link = link_element.get_attribute('href')

                    if title and link and link not in seen_articles:
                        articles.append({'title': title, 'link': link})
                        seen_articles.add(link)

                        print(f"Title: {title}\nLink: {link}\n")
                        print(scrape_article_bullet_points(driver, link))

                    if len(articles) >= max_articles:
                        break

                except Exception as e:
                    print(f"Error extracting article: {e}")

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")     
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'SearchResult-searchResultTitle')))

        driver.quit()

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

# Set up WebDriver options
chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
chrome_options.add_argument("--allow-insecure-localhost")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument('--disable-site-isolation-trials')
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

if not sign_in(driver):
    retry = 3
    for i in range(retry):
        print("Retry sign in attempt", i+1, "of 3")
        if sign_in(driver):
            break

try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'ProfileIcon-profileIconContainer'))
    )
    print("Session is maintained after sign-in.")
except TimeoutException:
    print("Session is not maintained after sign-in.")
    driver.quit()
    exit()

scrape_cnbc_search_results(driver, 'stocks', 1)

driver.quit()