import requests
import os
import json
import numpy as np
from listMake import list_Maker
from file_sanitizer import sanitize_filename


def check_site_google(url):
    api_key = "AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU"  # Directly using the API key
    cse_id = "a6d5af5008e9e4d57"  # Direct use of the CSE ID
    query = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={url}"
    base_dir = ".\SearchAnl\LocalJson\GoogleCustomSearch"  # Base directory for storing JSON files

    try:
        response = requests.get(query)
        response.raise_for_status()  # Raises an exception for 4XX and 5XX errors
        results = response.json()

        # Create the directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)

        # Construct file path with sanitized file name
        file_name = sanitize_filename(f"{url.replace('http://', '').replace('https://', '')}.json")
        file_path = os.path.join(base_dir, file_name)
        
        #Store Json
        with open(file_path, "w") as json_file:
            json.dump(results, json_file, indent=4)

        total_results = int(results.get("searchInformation", {}).get("totalResults", 0))
        if total_results > 0:
            return (True, total_results)
        else:
            return (False, 0)
    except requests.exceptions.RequestException as e:
        # Catch all requests exceptions
        return (False, f"Request error occurred: {e}")

if __name__ == "__main__":
    # example usage
    # 
    # url_to_check = "http://fb.com"
    test_phishing_sites=list_Maker("./SearchAnl/text/phishing_links_rate_limit.txt")
    # is_indexed, num_Results = check_site_google(url_to_check)
    count = len(test_phishing_sites)
    results_Array=[]
    for i, link in enumerate(test_phishing_sites):
        print("Iter: ", i) #visualise the api running , will run up to iter 100
        is_indexed, num_Results = check_site_google(link)
        results_Array.append(num_Results)

    #just to check the median and data distribution of search results from the different links
    test= np.array(results_Array)
    print(np.percentile(test,25)) #25 percentile (value=0)
    print(np.percentile(test,50)) #median (value=0)
    print(np.percentile(test,75)) #75 percentile (value=1)



