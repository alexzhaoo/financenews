from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv
import os
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables
load_dotenv()

CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH')

def sign_in(driver):
    try:
        driver.get('https://www.cnbc.com')

        sign_in_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//a[text()="SIGN IN"]'))
        )
        sign_in_link.click()
        #print("Clicked the SIGN IN link.")

        # Wait for the sign-in modal to be displayed
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'sign-in'))
        )
        #print("Sign-in modal is visible.")

        # Enter the username
        email_input = driver.find_element(By.NAME, 'email')
        email_input.send_keys('cnbcscrape@gmail.com')
        #print("Entered email.")

        # Enter the password
        password_input = driver.find_element(By.NAME, 'password')
        password_input.send_keys('Cnbc123!')
        #print("Entered password.")

        # Submit the form
        password_input.send_keys(Keys.RETURN)
        #print("Submitted the sign-in form.")

        # Wait for the sign-in process to complete
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ProfileIcon-profileIconContainer'))
        )
        print("Sign-in was successful.")
        return True
    except TimeoutException:
        print("Sign-in failed or took too long.")
        return False

def scrape_article_bullet_points(driver, article_url):
    driver.get(article_url)
    
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'ArticleBody-articleBody')))

    bullet_points = []
    try:
        # Debug log
        #print(f"Scraping article: {article_url}")

        # Find elements containing bullet points
        groups = driver.find_elements(By.CLASS_NAME, 'group')
        #print(f"Found {len(groups)} 'group' elements.")

        for group in groups:
            ul_elements = group.find_elements(By.TAG_NAME, 'ul')
            #print(f"Found {len(ul_elements)} 'ul' elements in group.")

            for ul in ul_elements:
                li_elements = ul.find_elements(By.TAG_NAME, 'li')
                #print(f"Found {len(li_elements)} 'li' elements in ul.")

                for li in li_elements:
                    bullet_points.append(li.text.strip())

        # Debug log
        #print(f"Bullet points from {article_url}: {bullet_points}")

    except Exception as e:
        print(f"Error extracting bullet points: {e}")

    return bullet_points

# Function to scrape search results data
def scrape_cnbc_search_results(query, max_articles):
    # Set up WebDriver options
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument('--ignore-ssl-errors')
    
    # Start the WebDriver
    service = Service(CHROMEDRIVER_PATH)
    global driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Open the CNBC search results page
    search_url = f'https://www.cnbc.com/search/?query={query}&qsearchterm={query}'
    driver.get(search_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'SearchResult-searchResultTitle')))  # Explicit wait

    # Comment out or remove the page source print statement
    # print(driver.page_source)
    articles = []
    seen_articles = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    # Find the search result items
    try:

        while len(articles) < max_articles:
            search_result_items = driver.find_elements(By.CLASS_NAME, 'SearchResult-searchResultTitle')
            
            for item in search_result_items:

                try:
                    # Extract title and link
                    link_element = item.find_element(By.CLASS_NAME, 'resultlink')

                    title = link_element.text.strip()
                    link = link_element.get_attribute('href')

                    # Append unique data
                    if title and link and link not in seen_articles:
                        articles.append({'title': title, 'link': link})
                        seen_articles.add(link) # Mark the article as seen

                        # Debug log
                        print(f"Title: {title}\nLink: {link}\n")
                    # Conditional needed because the articles scraped can exceed the max_articles in a single scroll
                    if len(articles) >= max_articles:
                        break

                except Exception as e:
                    print(f"Error extracting article: {e}")

            # Scroll down to the bottom of the page and load articles
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")     
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'SearchResult-searchResultTitle')))


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

# Set up WebDriver options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
chrome_options.add_argument("--allow-insecure-localhost")
# chrome_options.add_argument("--headless")  
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument('--ignore-ssl-errors')
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

if not sign_in(driver):
    retry = 3
    for i in range(retry):
        print("Retry sign in attempt", i+1, "of 3")
        if sign_in(driver):
            break

# Ensure the session is maintained by checking the profile icon
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'ProfileIcon-profileIconContainer'))
    )
    print("Session is maintained after sign-in.")
except TimeoutException:
    print("Session is not maintained after sign-in.")
    driver.quit()
    exit()

# Navigate to the article URL and check if the session is still active
driver.get('https://www.cnbc.com/2024/12/03/wednesdays-big-stock-stories-whats-likely-to-move-the-market.html?&qsearchterm=stocks')
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'ProfileIcon-profileIconContainer'))
    )
    print("Session is still active on the article page.")
except TimeoutException:
    print("Session is not active on the article page.")
    driver.quit()
    exit()

points = scrape_article_bullet_points(driver, 'https://www.cnbc.com/2024/12/03/wednesdays-big-stock-stories-whats-likely-to-move-the-market.html?&qsearchterm=stocks')
print(points)

driver.quit()