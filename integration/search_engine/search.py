import requests
import os
import json
# import numpy as np
# from listMake import list_Maker
# from file_sanitizer import sanitize_filename

def check_site_google(url):
    site_search = "site:" + url
    print(site_search)
    
    api_key = "AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU"  # Directly using the API key
    cse_id = "a6d5af5008e9e4d57"  # Direct use of the CSE ID
    query = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={url}"

    try:
        response = requests.get(query)
        response.raise_for_status()  # Raises an exception for 4XX and 5XX errors
        results = response.json()
        
        total_results = int(results.get("searchInformation", {}).get("totalResults",0))
        return total_results

    except requests.exceptions.RequestException as e:
        # Catch all requests exceptions
        return ("Request error occurred: {e}")

if __name__ == "__main__":
    # example usage
    url_to_check = "thehoneycombers.com"
    num_Results = check_site_google(url_to_check)
    print(num_Results)



