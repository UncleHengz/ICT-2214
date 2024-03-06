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
    "AvgMonthlyVisits":0,
    "GlobalRank":0,
    "CountryRank":0,
    "TrafficSources":{},
    "CountryCount":0, # From Countries key
    "SearchTerms":[]
}
for i in result:
    print(i) #check key names
print()
print(result["EstimatedMonthlyVisits"]) # Check data
filtDict["SiteName"]= result["SiteName"]
