try:
    from requests import get
    from urllib.parse import urlparse
    import random
except ImportError as err:
    print(f"Failed to import required modules {err}")

user_agents_list = [
    'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
]

def pretty_print_dict(d, indent=0):
    res = ""
    for k, v in d.items():
        res += "\t"*indent + str(k) + "\n"
        if isinstance(v, dict):
            res += pretty_print_dict(v, indent+1)
        else:
            res += "\t"*(indent+1) + str(v) + "\n"
    return res

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

if __name__ == "__main__":
    result = similarGet("https://www.cats.com")
    filtDict = {
        "SiteName": "",
        "TopCountryShares": [],
        "TotalVists": 0,
        "Category": "",
        "GlobalRank": 0,
        "HQCountry": "",
        "CountryRank": 0,
        "TrafficSources": {},
        "CountryCount": 0,
        "SearchTerms": []
    }

    filtDict["SiteName"] = result["SiteName"]

    for i in result["TopCountryShares"]:
        filtDict["TopCountryShares"].append(i["CountryCode"])

    filtDict["TotalVists"] = result.get("Engagements", {}).get("Visits", 0)

    filtDict["Category"] = result.get("Category", "")

    filtDict["GlobalRank"] = result.get("GlobalRank", 0)

    filtDict["HQCountry"] = result.get("CountryRank", {}).get("CountryCode", "")

    filtDict["CountryRank"] = result.get("CountryRank", {}).get("Rank", 0)

    filtDict["TrafficSources"] = result.get("TrafficSources", {})

    countryCount = len(result.get("Countries", []))

    filtDict["CountryCount"] = countryCount

    for i in result.get("TopKeywords", []):
        filtDict["SearchTerms"].append(i.get("Name", ""))

    print(pretty_print_dict(filtDict))
