#TODO : Check for values which are none and return boolean 

try:
    from requests import get
    from urllib.parse import urlparse
    import random
    import os
    import json 
    from file_sanitizer import sanitize_filename

except ImportError as err:
    print(f"Failed to import required modules {err}")

user_agents_list = [ #allows going through 403 error
    'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
]

#./text/keysforsimilarwebdict.txt shows what columns are available to retrieve
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
    base_dir = ".\SearchAnl\LocalJson\SimWeb"  # Base directory for storing JSON files

    if resp.status_code == 200:
        # Construct file path with sanitized file name
        file_name = sanitize_filename(f"{website.replace('http://', '').replace('https://', '')}.json")
        file_path = os.path.join(base_dir, file_name)
        #Store Json
        with open(file_path, "w") as json_file:
            json.dump(resp.json(), json_file, indent=4)
        return resp.json()
    else:
        resp.raise_for_status()
        return False

def filteredDict(SimWebJSON): #input is the output from similarGet()
    
    filtDict = {
        "SiteName": "",
        "TopCountryShares": [],
        "TotalVisits": 0,
        "Category": "",
        "GlobalRank": 0,
        "HQCountry": "",
        "CountryRank": 0,
        "TrafficSources": {},
        "SearchTerms": []
    }

    filtDict["SiteName"] = SimWebJSON["SiteName"]

    for i in SimWebJSON["TopCountryShares"]:
        filtDict["TopCountryShares"].append(i["CountryCode"])

    filtDict["TotalVisits"] = SimWebJSON.get("Engagements", {}).get("Visits", 0)

    filtDict["Category"] = SimWebJSON.get("Category", "")

    filtDict["GlobalRank"] = SimWebJSON.get("GlobalRank", 0)

    filtDict["HQCountry"] = SimWebJSON.get("CountryRank", {}).get("CountryCode", "")

    filtDict["CountryRank"] = SimWebJSON.get("CountryRank", {}).get("Rank", 0)

    filtDict["TrafficSources"] = SimWebJSON.get("TrafficSources", {})

    for i in SimWebJSON.get("TopKeywords", []):
        filtDict["SearchTerms"].append(i.get("Name", ""))

    return filtDict

def SussyChecker(SimDict): # take the filteredDict as input
    Suspicious = 0

    if SimDict["TotalVisits"]==0: 
        #check total visits recorded , if not tracked, could be not well known site
        Suspicious +=1

    if (SimDict["GlobalRank"]['Rank'] is None) or (SimDict["CountryRank"] is None):  
        #if trackable, the type will be int instead of none
        Suspicious +=1

    if SimDict["HQCountry"] is None: #if traceable should be a string instead
        Suspicious +=1

    trafficTracker=0 
    # used to track the percentage of traffic from a specific media ,
    # if untrackable , might have chance of being phising site as not well known 
    for i in SimDict["TrafficSources"]:
        if (SimDict["TrafficSources"][i] is None):
            Suspicious+=1
        else:    
            trafficTracker+=SimDict["TrafficSources"][i]
            print(trafficTracker)
            if trafficTracker==0:
                Suspicious +=1
    
    if len(SimDict["SearchTerms"])==0:
        Suspicious+=1

    return Suspicious

if __name__ == "__main__":
    result = similarGet("http://grub-terbaruyoutuber-freefiregarena1.duckdns.org/index.php")
    filtDict=filteredDict(result)
    print(SussyChecker(filtDict))
    # print(filtDict["Category"])
    print(filtDict.keys())