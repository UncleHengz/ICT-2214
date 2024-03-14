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

        # Check if any threats were found
        if 'matches' in result:
            print(f"Threats found for {url}:")
            for threat in result['matches']:
                print(f"- {threat['threatType']}")
            return False, "Threats found"  # Indicates threats were found, URL is not safe
        else:
            print(f"No threats found for {url}.")
            return True, "No threats found"  # Indicates no threats were found, URL is safe

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return False, f"HTTP error occurred: {http_err}"  # Indicates an error occurred, status of URL is uncertain
    except Exception as err:
        print(f"An error occurred: {err}")
        return False, f"An error occurred: {err}"  # Indicates an error occurred, status of URL is uncertain


api_key = 'AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU'

if __name__=="__main__":    
    # can have a file containing malicious links to check which links got issue 
    for i in test_array:
        check_url_safe(api_key,i)


