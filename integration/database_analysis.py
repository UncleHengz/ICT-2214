import requests
from bs4 import BeautifulSoup

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

def database_analysis(received_domain):
    phishing_links = []
    with open('ALL-phishing-links.txt','r',encoding='utf-8') as file:
        for item in file:
            phishing_links.append(item.strip())
        file.close()
    is_malicious = False
    #Code for the link extraction and comparison start
    # reqs = requests.get(received_domain)
    # soup = BeautifulSoup(reqs.text, 'html.parser')
    soup = fetch_and_parse_content(received_domain)
    urls = []
    for link in soup.find_all('a'):
        urls.append(link.get('href'))
    match = list(set(phishing_links) & set(urls))
    #Code for link extraction and comparison end
    if received_domain in phishing_links or match: #Added or operator to ensure if the links on the site is phishing then its malicious as well
        is_malicious = True # malicious
    return is_malicious
