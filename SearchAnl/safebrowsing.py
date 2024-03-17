import requests
from listMake import list_Maker

testfilepath="./SearchAnl/safebrowsetestsites.txt"

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
        response = requests.post(endpoint, params=params, json=payload)
        response.raise_for_status()
        result = response.json()

        unique_threats = set()  # Use a set to store unique threats

        # print(result)# code to validate keys
        # print("\n\n\n\n")
        # print(result['matches'])# code to validate keys
        if 'matches' in result:
            for threat in result['matches']:
                unique_threats.add(threat['threatType'])
            
            if unique_threats:
                print(f"\nThreats found for {url}")
                for threat in unique_threats:
                    print(f"- {threat}")
                return False, "Threats found"
            else:
                return True, "No threats found"
        else:
            print(f"\nNo threats found for {url}")
            return True, "No threats found"
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return False, f"HTTP error occurred: {http_err}"
    except Exception as err:
        print(f"An error occurred: {err}")
        return False, f"An error occurred: {err}"  # Indicates an error occurred, status of URL is uncertain


api_key = 'AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU'

if __name__=="__main__":    
    for i in list_Maker(testfilepath):
        check_url_safe(api_key,i)


