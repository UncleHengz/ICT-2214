import requests
import os
import json
import search_engine.simweb as simweb

api_key = 'AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU'
search_details = {
    "Site Index": False,
    "Google Safe Browsing": False,
    "Similar Web": False
}


def check_site_google(url):
    site_search = "site:" + url

    cse_id = "a6d5af5008e9e4d57"  # Direct use of the CSE ID
    query = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={site_search}"

    try:
        response = requests.get(query)
        response.raise_for_status()  # Raises an exception for 4XX and 5XX errors
        results = response.json()
        
        total_results = int(results.get("searchInformation", {}).get("totalResults",0))
        
        return total_results

    except Exception as err:
        print(f"Error: {err}")
        return None
    
    
def check_url_safe(url):
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
                # for threat in unique_threats:
                #     print(f"- {threat}")
                return True
        else:
            return False
    except Exception as err:
        print(f"Error: {err}")
        return None

def assess_phishing_risk(url):
    suspicion_score = 0
    
    # Check if the site is indexed by Google
    num_results = check_site_google(url)
    if num_results is None:
        return None
    elif num_results<=50: 
        suspicion_score += 1
        search_details["Site Index"] = True
        
    # Check against Google's Safe Browsing API
    match_result = check_url_safe(url)
    if match_result is None:
        return None
    elif match_result == True:
        suspicion_score += 3  
        search_details["Google Safe Browsing"] = True
    
    # Calls similarweb API to check ranking, category etc
    response = simweb.similarAPI(url)
    if response is not None:
        filtDict = simweb.filteredDict(response)
        simweb_result = simweb.SimWebChecker(filtDict)
        if simweb_result == True:
            suspicion_score += 2
            search_details["Similar Web"] = True
    else:
        return None
            
    # Combine results to make a final assessment
    if suspicion_score >= 3: 
        return True, search_details
    else:
        return False, search_details