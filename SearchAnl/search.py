import requests
import math
from listMake import list_Maker
sum=0
count=0
def check_site_google(url):
    api_key = "AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU"  # Directly using the API key
    cse_id = "a6d5af5008e9e4d57"  # Direct use of the CSE ID
    query = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={url}"

    try:
        response = requests.get(query)
        response.raise_for_status()  # Raises an exception for 4XX and 5XX errors
        results = response.json()
        total_results = int(results.get("searchInformation", {}).get("totalResults", 0))
        if total_results > 0:
            return (True, total_results)
        else:
            return (False, 0)
    except requests.exceptions.RequestException as e:
        # Catch all requests exceptions
        return (False, f"Request error occurred: {e}")

if __name__ == "__main__":
    # url_to_check = "http://fb.com"
    test_phishing_sites=list_Maker("./SearchAnl/phishing_links_real_sample.txt")
    # is_indexed, num_Results = check_site_google(url_to_check)
    count = len(test_phishing_sites)
    for i, link in enumerate(test_phishing_sites):
        print("Iter: ", i)
        is_indexed, num_Results = check_site_google(link)
        sum+=num_Results
    avg = sum/count
    print(avg)
    

