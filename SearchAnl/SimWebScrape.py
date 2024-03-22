from urllib.parse import urlparse
from bs4 import BeautifulSoup
import rpa as r
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pandas as pd
from urllib.parse import urlparse
import requests





# def test(url):
#     user_agents = [
#         # Add more updated user agents here
#         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
#         'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
#         'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
#     ]
#     headers = {
#         'User-Agent': random.choice(user_agents),
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#         'Accept-Language': 'en-US,en;q=0.5',
#         'Referer': 'https://www.google.com/',
#         'DNT': '1', # Do Not Track Request Header
#         'Connection': 'keep-alive',
#         'Upgrade-Insecure-Requests': '1',
#         'TE': 'Trailers',
#     }
#     with requests.Session() as session:
#         session.headers.update(headers)
#         try:
#             response = session.get(url, timeout=10) # Use a timeout for the request
#             if response.status_code == 200:
#                 time.sleep(random.uniform(1, 5))  # Adjust delay to be more random
#                 soup = BeautifulSoup(response.text, 'html.parser')
#                 return soup.prettify()
#             else:
#                 print(f"Error accessing {url}: Status Code {response.status_code}")
#                 return None
#         except requests.exceptions.RequestException as e:
#             print(f"Request failed: {e}")
#             return None

# # Example Usage
# domain_url = get_domain("https://www.amazon.com")
# similarweb_url = f"https://www.similarweb.com/website/{domain_url}/#overview"
# print(test(similarweb_url))

#-----------------------------------
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# import pandas as pd
# from urllib.parse import urlparse
# import requests

def get_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain

#Please download the following driver 
# requires chrome to be updated to version 123  
# https://storage.googleapis.com/chrome-for-testing-public/123.0.6312.58/win64/chromedriver-win64.zip
service = Service(executable_path="./SearchAnl/chromedriver/chromedriver.exe")
driver = webdriver.Chrome(service=service)
domain_url=(get_domain("https://www.amazon.com"))[4:]
similarweb_url = f"https://www.similarweb.com/website/{domain_url}/#overview"
print(similarweb_url)
driver.get(similarweb_url)

