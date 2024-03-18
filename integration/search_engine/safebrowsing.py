import requests
import json
import os

def check_url_safe(url):
    api_key = 'AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU'
    # Google Safe Browsing API endpoint
    endpoint = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    
    # Parameters for the API request
    payload = {
        "client": {
            "clientId": "my_safeBrowsing_checker",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING","THREAT_TYPE_UNSPECIFIED","UNWANTED_SOFTWARE","POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["PLATFORM_TYPE_UNSPECIFIED","WINDOWS", "LINUX","ANDROID","OSX","IOS","ANY_PLATFORM","ALL_PLATFORMS","CHROME"],
            "threatEntryTypes": ["URL","THREAT_ENTRY_TYPE_UNSPECIFIED","EXECUTABLE"],
            "threatEntries": [
                {"url": url}
            ]
        }
    }

    # Complete URL with the API key
    params = {'key': api_key}
    unique_threats = set()
    
    try:
        response = requests.post(endpoint, params=params, json=payload)
        response.raise_for_status()
        result = response.json()

        if 'matches' in result:
            for threat in result['matches']:
                unique_threats.add(threat['threatType'])
            
            if unique_threats:
                print(f"\nThreats found for {url}")
                for threat in unique_threats:
                    print(f"- {threat}")
                return True, "Threats found"
        else:
            return False, "No threats found"
    except requests.exceptions.HTTPError as http_err:
        return None, f"HTTP error occurred: {http_err}"
    except Exception as err:
        return None, f"An error occurred: {err}"  # Indicates an error occurred, status of URL is uncertain

if __name__=="__main__":  
    url = "acc-mercari.com"  
    is_malicious, message = check_url_safe(url)
    if is_malicious is None:
        print(message)

