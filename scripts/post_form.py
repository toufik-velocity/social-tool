import requests
from bs4 import BeautifulSoup
import json, uuid

# login_url = "https://social.velocitystudio.dev/"  # Replace with the actual login URL
# form_url = "https://social.velocitystudio.dev/Bmifxmgtfwi/Bmsj%7Cdutxydrfszfqq~"

login_url = "http://127.0.0.1:8000/"  # Replace with the actual login URL
form_url = "http://127.0.0.1:8000/Bmifxmgtfwi/Bmsj%7Cdutxydrfszfqq~"

# Create a session to maintain cookies
session = requests.Session()

# Perform a GET request to retrieve the CSRF token from the login page
login_page_response = session.get(login_url)
login_page_response.raise_for_status()

# Parse the HTML to extract the CSRF token
soup = BeautifulSoup(login_page_response.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

# Replace these values with the actual login credentials
login_data = {
    "csrfmiddlewaretoken": csrf_token,
    "username": "SamuelKings",  # Replace with your actual username
    "password": "Password#1"   # Replace with your actual password
}

# Perform the POST request to login
headers = {
    "Referer": login_url,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
login_response = session.post(login_url, headers=headers, data=login_data)
login_response.raise_for_status()

# Check if login was successful by checking the response URL or content
if login_response.url == login_url or "Login" in login_response.text:
    print("Login failed. Please check your credentials.")
else:
    print("Login successful.")  

    # Now perform a GET request to retrieve the CSRF token for the form page
    form_page_response = session.get(form_url)
    form_page_response.raise_for_status()

    # Parse the HTML to extract the CSRF token
    soup = BeautifulSoup(form_page_response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

    comments = json.dumps([{"likes": 10, "username": "user1", "timestamp": "2024-07-17T12:34:56Z", "comment_text": "This is a comment."}, {"likes": 5, "username": "user2", "timestamp": "2024-07-17T12:35:56Z", "comment_text": "This is another comment."}])
    comments = json.dumps([
    {
      "comment_id": 0,
      "comment_text": "I would love one too",
      "commentator": "Angela White",
      "replies": [
        {
          "reply_id": 0,
          "replier": "Dihan Rahman",
          "reply": "Angela White ore mathar cod ......"
        },
        {
          "reply_id": 1,
          "replier": "Kiloa Zoldik",
          "reply": "Angela White Oui 🤣❤️"
        },
        ]}])
    # Replace these values with the actual data you want to submit
    data = {
        "csrfmiddlewaretoken": csrf_token,
        "platform_id": "Facebook",
        "post_date": "2024-07-24",  # Adjust the date format if necessary
        "user_id": "12345",
        "username": "john_doe",
        "content_type": "Text",
        "content": "This is a sample post content.",
        "url": "https://example.com/sample-post",
        "post_id": "post123",
        "likes": 100,
        "shares": 10,
        "num_comments": 5,
        "comments": comments,
    }

    # Perform the POST request with the form data
    response = session.post(form_url, headers=headers, data=data)

    # Print the response status and content
    print(f"Response Status Code: {response.status_code}")
    print("Response Headers:", response.headers)
    print("Response Content:", response.text)

    response.raise_for_status()
