import csv
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException
from dotenv import load_dotenv
import time
import datetime
import mysql.connector

# Load environment variables
load_dotenv()

# Connect to MySQL database
sql_password = os.getenv('SQL_PASS')
conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=sql_password,
    database="cnbc"
)
cursor = conn.cursor()
print("Connected to the database successfully!")

CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE_PATH = os.path.join(SCRIPT_DIR, '../cookies.json')  # Path to the cookies file

if not os.path.exists(COOKIES_FILE_PATH):
    print(f"Cookies file not found at {COOKIES_FILE_PATH}")

# Loading cookies to bypass reCaptchas
def load_cookies(driver, cookies_file_path):
    with open(cookies_file_path, 'r') as cookies_file:
        cookies = json.load(cookies_file)
        for cookie in cookies:
            if 'sameSite' in cookie:
                del cookie['sameSite']
            if 'domain' in cookie:
                cookie['domain'] = '.cnbc.com'
            driver.add_cookie(cookie)

def sign_in(driver):
    try:
        driver.get('https://www.cnbc.com')
        load_cookies(driver, COOKIES_FILE_PATH)
        driver.refresh()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ProfileIcon-profileIconContainer'))
        )
        print("Sign-in was successful using cookies.")
        return True
    except TimeoutException:
        print("Sign-in failed or took too long.")
        return False

def scrape_article_bullet_points(driver, article_url):
    try:
        driver.get(article_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'ArticleBody-articleBody')))
        article_body = driver.find_element(By.CLASS_NAME, 'ArticleBody-articleBody')
        scraped_text = article_body.get_attribute('outerHTML')
        #print(f"Debugging article body HTML:\n{article_body.get_attribute('outerHTML')}")

    except (TimeoutException, WebDriverException) as e:
        print(f"Extracted Nothing: {e}")
        scraped_text = None
    
    return scraped_text

def scrape_cnbc_search_results(driver, query, max_articles):
    search_url = f'https://www.cnbc.com/search/?query={query}&qsearchterm={query}'
    driver.get(search_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'SearchResult-searchResultTitle')))
    articles = []
    seen_articles = set()
    retries = 3  # Number of retries for stale element references

    while len(articles) < max_articles:
        try:
            # Refresh element references in each loop to avoid stale references
            search_result_eyebrows = driver.find_elements(By.CLASS_NAME, 'SearchResult-searchResultEyebrow')
            search_result_items = driver.find_elements(By.CLASS_NAME, 'SearchResult-searchResultTitle')
            subscription_keywords = ["PRO:", "CNBC", "CLUB"]

            for item, eyebrow in zip(search_result_items, search_result_eyebrows):
                retry_count = 0
                while retry_count < retries:
                    try:
                        link_element = item.find_element(By.CLASS_NAME, 'resultlink')
                        title = link_element.text.strip()
                        link = link_element.get_attribute('href')

                        if title and link and link not in seen_articles:
                            seen_articles.add(link)

                            eyebrow_text = eyebrow.text.strip()
                            need_subscription = any(word in eyebrow_text.upper() for word in subscription_keywords)

                            if not need_subscription:
                                articles.append({'title': title, 'link': link})
                                print(f"Title: {title}")
                                print(f"Link: {link}")
                        break  # Exit retry loop on success
                    except StaleElementReferenceException:
                        retry_count += 1
                        print(f"Stale element exception caught. Retrying ({retry_count}/{retries})...")
                        time.sleep(1)  # Short delay before retry
                        # Refresh the DOM elements
                        search_result_items = driver.find_elements(By.CLASS_NAME, 'SearchResult-searchResultTitle')
                        search_result_eyebrows = driver.find_elements(By.CLASS_NAME, 'SearchResult-searchResultEyebrow')
                if retry_count == retries:
                    print("Max retries reached. Skipping element.")
            # Scroll down the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for new content to load

            # Break the loop if we have enough articles
            if len(articles) >= max_articles:
                break
        except TimeoutException:
            print("Timeout occurred while loading search results. Exiting.")
            break

    return articles
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
today_date = datetime.date.today().strftime('%Y-%m-%d')
try:
    if sign_in(driver):
        query = "stocks"
        max_articles = 4
        articles = scrape_cnbc_search_results(driver, query, max_articles)

        print(f"Scraped {len(articles)} articles. Fetching contents...")
        
        for article in articles:
            article_text = scrape_article_bullet_points(driver, article['link'])
            print(article)
            '''article['content'] = article_text  # Add scraped content to the article dictionary
            sqlquery = "INSERT INTO scraped_data (title, url, date_scraped, text_scraped) VALUES (%s,%s,%s,%s)"

            try: # Articles with no content scraped won't be added to the db
                print('writing article: ',article['title'], 'to csv')
                #print(article)
                data = (article['title'], article['link'],today_date, article['content'])
                cursor.execute(sqlquery, data)
                conn.commit()
            except:
                print('Article: ',article, 'cannot be written as no content was scraped.')
                continue'''
            

finally:
    driver.quit()


''' # For debugging purposes
# Print all the current data
cursor.execute("SELECT * FROM scraped_data")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.execute("TRUNCATE TABLE scraped_data;") # Clear the db
'''
print('scraped', len(articles),'articles')
# Close SQL database connection 
cursor.close()
conn.close()

driver.quit()
