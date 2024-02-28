# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests

def check_site_google(url):
    api_key = "AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU" # google custom search json api key
    cse_id = "a6d5af5008e9e4d57" #custom search engine id
    query = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={url}"
    response = requests.get(query)
    results = response.json()
    # print(results)

    # Check if there are any search results
    if results.get("searchInformation") and int(results.get("searchInformation").get("totalResults", 0)) > 0:
        return True, ("The site is indexed by Google. Total = " + str(int(results.get("searchInformation").get("totalResults"))) +" results found")
    else:
        return False, "The site is not indexed by Google."


if __name__ == '__main__':
    is_indexed, message = check_site_google("http://www.cloud4sal3xoxoMeow.com/")
    #can try with other sites
    #isIndexed is a boolean
    #message is whether indexed

    print(message)