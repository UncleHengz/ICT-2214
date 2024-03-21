from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests

def get_domain(url):
    # Parse the URL
    parsed_url = urlparse(url)
    # Extract the domain
    domain = parsed_url.netloc
    return domain

def test(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    url= "https://www.similarweb.com/website/" + get_domain(url) + "/#overview"
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup.prettify()

# Example Usage
print(test("https://www.facebook.com"))
