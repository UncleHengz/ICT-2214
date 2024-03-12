import requests


test_array= []
with open("./SearchAnl/testsites.txt") as my_file:
    for line in my_file:
        test_array.append(line)

def check_url_safe(api_key, url):
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

    try:
        # Make the POST request to the Safe Browsing API
        response = requests.post(endpoint, params=params, json=payload)
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX
        result = response.json()

        # Improved handling for empty results
        if 'matches' in result:
            print(f"Threats found for {url}:")
            for threat in result['matches']:
                print(f"- {threat['threatType']}")
        else:
            print(f"No threats found for {url}.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

api_key = 'AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU'
url_tocheck = 'https://www.singaporetech.edu.sg/careernexus/jobs'  # Replace with the URL you want to check

for i in test_array:
    check_url_safe(api_key,i)

