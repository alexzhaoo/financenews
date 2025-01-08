import csv
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from dotenv import load_dotenv
import time

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
    driver.get(article_url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'ArticleBody-articleBody')))
    #bullet_points = []
    try:
        article_body = driver.find_element(By.CLASS_NAME, 'ArticleBody-articleBody')
        scraped_text = article_body.get_attribute('outerHTML')
        #print(f"Debugging article body HTML:\n{article_body.get_attribute('outerHTML')}")

    except Exception as e:
        print(f"Error extracting bullet points: {e}")
    
    return scraped_text

def scrape_cnbc_search_results(driver, query, max_articles):
    search_url = f'https://www.cnbc.com/search/?query={query}&qsearchterm={query}'
    driver.get(search_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'SearchResult-searchResultTitle')))
    articles = []
    seen_articles = set()
    retries = 3  # Number of retries for stale element references
    try:
        while len(articles) < max_articles:
            search_result_eyebrows = driver.find_elements(By.CLASS_NAME, 'SearchResult-searchResultEyebrow')
            search_result_items = driver.find_elements(By.CLASS_NAME, 'SearchResult-searchResultTitle')
            subscription_keywords = ["PRO:", "CNBC", "CLUB"]
            
            #for item in search_result_items:
            for item, eyebrow in zip(search_result_items, search_result_eyebrows):
                try:
                    
                    link_element = item.find_element(By.CLASS_NAME, 'resultlink')
                    title = link_element.text.strip()
                    link = link_element.get_attribute('href')

                    if title and link and link not in seen_articles:
                        seen_articles.add(link)

                        eyebrow_text = eyebrow.text.strip()
                        need_subscription = any(word in eyebrow_text.upper() for word in subscription_keywords) # checks if the artricle card requires subscription to read
                        
                        if not need_subscription:
                            articles.append({'title': title, 'link': link})
                            print(f"Title: {title}\nLink: {link} does not require subscription")
                            scraped_text = scrape_article_bullet_points(driver, link)
                            articles[-1]['article text'] = scraped_text # adds text to the last article in the list
                            
                        else:
                            print(f"Skipping {link} because subscription is required")
                        if len(articles) >= max_articles:
                            break

                except StaleElementReferenceException:
                    print("Stale element reference exception caught. Retrying...")
                    retries -= 1
                    if retries > 0:
                        driver.get(search_url)  # Reload the search results page
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'SearchResult-searchResultTitle')))
                        time.sleep(1)
                    else:
                        print("Max retries reached. Exiting...")
                        break

                except Exception as e:
                    print(f"Error extracting article: {e}")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    except Exception as e:
        print(f"Error finding the search results: {e}")
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

# Sign in with cookies to avoid Captcha errors
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

# Open the CSV file once and write incrementally
file_name = 'CNBCSearchResults_with_BulletPoints.csv'
with open(file_name, 'w', encoding='utf-8', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, fieldnames=['title', 'link', 'article text'])
    dict_writer.writeheader()

    articles = scrape_cnbc_search_results(driver, 'stocks', 2)
    for article in articles:
        print('writing article: ',article['title'], 'to csv')
        dict_writer.writerow(article)
        

driver.quit()
