from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless Chrome (without GUI)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Set the path for the ChromeDriver
webdriver_service = Service('/usr/bin/chromedriver')  # Update with your actual path

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Navigate to the Facebook video page
url = "https://www.facebook.com/100044296486382/videos/358907080069233/?__so__=watchlist&__rv__=video_home_www_playlist_video_list"
driver.get(url)
print(driver.page_source)

# Wait for the page to load completely
time.sleep(5)  # Adjust the sleep time as necessary

# Extract the necessary data
# Note: The actual selectors may need to be adjusted based on the page's structure

# Example of extracting some data (update selectors based on actual page structure)
try:
    post_date_element = driver.find_element(By.CSS_SELECTOR, "div[data-testid='story-subtitle'] span")
    post_date = post_date_element.text  # Adjust extraction logic as needed
except:
    post_date = "Unknown"

try:
    username_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Cristiano Ronaldo')]")
    username = username_element.text  # Adjust extraction logic as needed
except:
    username = "Unknown"

try:
    likes_element = driver.find_element(By.CSS_SELECTOR, "span[class='pcp91wgn']")
    likes = int(likes_element.text.replace(',', ''))  # Adjust extraction logic as needed
except:
    likes = 0

try:
    shares_element = driver.find_element(By.CSS_SELECTOR, "span[class='pcp91wgn']")
    shares = int(shares_element.text.replace(',', ''))  # Adjust extraction logic as needed
except:
    shares = 0

# Wait for the span element to be present
try:
    span_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'comments')]"))
    )
    full_text = span_element.text
    print("Full text found:", full_text)
    
    # Extract the part of the text before the word "comments"
    if "comments" in full_text:
        text_before_comments = full_text.split(" comments")[0]
        print("Text before 'comments':", text_before_comments)
    else:
        print("The word 'comments' was not found in the text.")
except Exception as e:
    print(f"Error finding the span element: {e}")

try:
    comments_element = driver.find_element(By.CSS_SELECTOR, "span[class='pcp91wgn']")
    num_comments = int(comments_element.text.replace(',', ''))  # Adjust extraction logic as needed
except:
    num_comments = 0

# Example comments extraction logic (update selectors based on actual page structure)
comments = []
try:
    comment_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='UFI2Comment/body']")
    for comment in comment_elements:
        comment_text = comment.find_element(By.CSS_SELECTOR, "span").text
        username = comment.find_element(By.CSS_SELECTOR, "a").text
        timestamp = comment.find_element(By.CSS_SELECTOR, "abbr").get_attribute("data-utime")
        likes = int(comment.find_element(By.CSS_SELECTOR, "span[aria-label*='like']").text.replace(',', ''))
        comments.append({"likes": likes, "username": username, "timestamp": timestamp, "comment_text": comment_text})
except:
    comments = []

data = {
    "csrfmiddlewaretoken": "csrf_token_placeholder",  # Placeholder for CSRF token
    "platform_id": "Facebook",
    "post_date": post_date,
    "user_id": "12345",  # Example user ID
    "username": username,
    "content_type": "Text",  # Example content type
    "content": "This is a sample post content.",  # Example content
    "url": url,
    "post_id": "post123",  # Example post ID
    "likes": likes,
    "shares": shares,
    "num_comments": num_comments,
    "comments": comments,
}

# Print the collected data
print(data)

# Close the browser
driver.quit()
