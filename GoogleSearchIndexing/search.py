
# # similiarweb api key:0ec16759045a4290800ff27abebc07b6

# import requests
# from urllib.parse import urlparse
# def extract_domain(url):
#     parsed_url = urlparse(url)
#     domain = parsed_url.netloc
#     if domain.startswith('www.'):
#         domain = domain[4:]
#     return domain

# siteinfo = {
#     "url":"",
#     "information":
#     {
#         "indexd":"no",
#         "ranking": 0
#     }
# }

# def check_site_google(url):

#     api_key = "AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU" # google custom search json api key
#     cse_id = "a6d5af5008e9e4d57" #custom search engine id
#     query = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={url}"
#     response = requests.get(query)
#     results = response.json()
#     print(results["items"])
#     for i in results["items"]:
#         print("_________")
#         for x in i:

#             print(x,":",i[x])

#     # Check if there are any search results
#     if results.get("searchInformation") and int(results.get("searchInformation").get("totalResults", 0)) > 0:
#         return True, ("The site is indexed by Google. Total = " + str(int(results.get("searchInformation").get("totalResults"))) +" results found")
#     else:
#         return False, "The site is not indexed by Google."

# def print_dict(d, indent):
#     for key, value in d.items():
#         print(' ' * indent + str(key) + ':', end=' ')
#         if isinstance(value, dict):
#             print()  # Print a newline if the value is a dictionary
#             print_dict(value, indent + 4)  # Recursively print the nested dictionary with increased indentation
#         else:
#             print(value)  # Print the value

#  # todo: main thing is to find ranking of site
# if __name__ == '__main__':
#     # is_indexed, message = check_site_google("https://amaonz.xjijin.com.cn")
#     test=extract_domain('www.mofunzone.com')
#     print(test)
#     #can try with other sites
#     #isIndexed is a boolean
#     #message is whether indexed

# import requests

#wanted to try similarweb api but expired api (7 days)
# url = "https://api.similarweb.com/v3/batch/traffic_and_engagement/request-report"

# payload = {
#     "metrics": ["all_traffic_visits", "global_rank", "desktop_new_visitors", "mobile_average_visit_duration"],
#     "filters": {
#         "domains": ["facebook.com"],
#         "countries": ["WW"],
#         "include_subdomains": True
#     },
#     "granularity": "monthly",
#     "start_date": "2022-06",
#     "end_date": "2023-06",
#     "response_format": "csv",
#     "delivery_method": "download_link"
# }
# headers = {
#     "accept": "application/json",
#     "content-type": "application/json",
#     "api-key": "a6c8066af27840b2a37cf72fbe6ec2b9"
# }

# response = requests.post(url, json=payload, headers=headers)

# print(response.text)
    

try:
    from requests import get
    from urllib.parse import urlparse
    import random
    

except ImportError as err:
    print(f"Failed to import required modules {err}")

user_agents_list = [ # allow us to bypass 403 error
    'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
]

def similarGet(website):
    domain = '{uri.netloc}'.format(uri=urlparse(website))
    domain = domain.replace("www.", "")
    ENDPOINT = 'https://data.similarweb.com/api/v1/data?domain=' + domain
    resp = get(ENDPOINT, headers={'User-Agent': random.choice(user_agents_list)})

    if resp.status_code == 200:
        return resp.json()
    else:
        resp.raise_for_status()
        return False
    
result = similarGet("http://www.facebook.com")
filtDict ={
    "SiteName":"",
    "TopCountryShares":[], # can find out top 5 country affected , only need country code
    "Engagments":"",
    "EstimatedMonthlyVisits":0,
    "GlobalRank":0,
    "CountryRank":0,
    "TrafficSources":{},
    "CountryCount":0,
    "SearchTerms":[]
}
print(result["SiteName"])
filtDict["SiteName"]= result["SiteName"]