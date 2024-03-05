
# similiarweb api key:0ec16759045a4290800ff27abebc07b6

import requests
from urllib.parse import urlparse
def extract_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain


def check_site_google(url):
    api_key = "AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU" # google custom search json api key
    cse_id = "a6d5af5008e9e4d57" #custom search engine id
    query = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={url}"
    response = requests.get(query)
    results = response.json()
    print(results["items"])
    for i in results["items"]:
        print("_________")
        for x in i:

            print(x,":",i[x])

    # Check if there are any search results
    if results.get("searchInformation") and int(results.get("searchInformation").get("totalResults", 0)) > 0:
        return True, ("The site is indexed by Google. Total = " + str(int(results.get("searchInformation").get("totalResults"))) +" results found")
    else:
        return False, "The site is not indexed by Google."

def print_dict(d, indent):
    for key, value in d.items():
        print(' ' * indent + str(key) + ':', end=' ')
        if isinstance(value, dict):
            print()  # Print a newline if the value is a dictionary
            print_dict(value, indent + 4)  # Recursively print the nested dictionary with increased indentation
        else:
            print(value)  # Print the value

 # todo: main thing is to find ranking of site
if __name__ == '__main__':
    is_indexed, message = check_site_google("https://amaonz.xjijin.com.cn")
    #can try with other sites
    #isIndexed is a boolean
    #message is whether indexed

    print(message)