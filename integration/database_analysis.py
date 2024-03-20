import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def fetch_and_parse_content(url):
    try:
        # Try with https://
        response = requests.get('https://' + url)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.RequestException:
        try:
            # Try with http://
            response = requests.get('http://' + url)
            response.raise_for_status()  # Check for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except requests.RequestException as e:
            print(f"Failed to fetch content for {url}: {e}")
            return None
        
# Function to extract domain name from URL
def extract_domain(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc:
        return parsed_url.netloc.split(':')[0]  # Remove port number if present
    else:
        return None

def database_scan(received_domain):
    phishing_links = []
    # Open and read phishing links file
    try:
        with open('ALL-phishing-links.txt', 'r', encoding='utf-8') as file:
            for item in file:
                phishing_links.append(item.strip())
            file.close()
    except Exception as e:
        print("Error reading phishing links file:", e)
        # Handle the error, e.g., exit the program or set default phishing links
        file.close()
        return None
        
    is_malicious = False
    match = None
    
    try:
        #Code for the link extraction and comparison start
        soup = fetch_and_parse_content(received_domain)
        urls = []
        all_links = soup.find_all('a')
        if all_links:
            for link in all_links:
                urls.append(link.get('href'))
            # Extract domain names and filter unique ones
            unique_domains = set(filter(None, map(extract_domain, urls)))

            # Comparison with phishing links database
            match = list(set(phishing_links) & set(unique_domains))
            #Code for link extraction and comparison end
        if received_domain in phishing_links or match: #Added or operator to ensure if the links on the site is phishing then its malicious as well
            is_malicious = True # malicious
    except Exception as e:
        print("Error occurred during link extraction and comparison:", e)
        return None
    
    return is_malicious


