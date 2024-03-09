import requests
import json

#TODO fix code

API_KEY = 'AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU'
API_URL = 'https://safebrowsing.googleapis.com/v4/threatMatches:find'

def check_url(url):
    payload = {
        "client": {
            "clientId": "your_client_id",
            "clientVersion": "1.0.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "THREAT_TYPE_UNSPECIFIED"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(API_KEY)
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if 'matches' in data:
            # URL is malicious
            return True
        else:
            # URL is safe
            return False
    else:
        # Handle error response
        print("Error:", response.status_code)
        return False

# Example usage
url_to_check = "https://www.google.com"
if check_url(url_to_check):
    print("The URL is malicious")
else:
    print("The URL is safe")
