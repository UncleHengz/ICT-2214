
from requests import get
import random
import os
import json 
import re

user_agents_list = [ #allows going through 403 error
    'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
]

def similarAPI(domain_link):
    pattern = r'(?:(?:https?:\/\/)?(?:www\.)?([^\/\n]+))'
    # Use re.search to find the domain part in the link
    domain = re.search(pattern, domain_link).group(1)

    ENDPOINT = 'https://data.similarweb.com/api/v1/data?domain=' + domain
    try:
        resp = get(ENDPOINT, headers={'User-Agent': random.choice(user_agents_list)})
        
        if resp.status_code == 200:
            return resp.json()
        else:
            resp.raise_for_status()
            return None
    except Exception as err:
        print(f"Error: {err}")
        return None

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

def SimWebChecker(resultDict): # take the filteredDict as input
    suspicion_score = 0

    if resultDict["TotalVisits"] < 100: #check total visits recorded , if not tracked, could be not well known site
        suspicion_score +=1

    if (resultDict["GlobalRank"]['Rank'] is None) or (resultDict["CountryRank"] is None):  #if trackable, the type will be int instead of none
        suspicion_score +=1

    if resultDict["HQCountry"] is None: #if traceable should be a string instead
        suspicion_score +=1

    trafficTracker=0 # used to track the percentage of traffic from a specific media , if untrackable , might have chance of being phising site as not well known 
    for i in resultDict["TrafficSources"]:
        if (resultDict["TrafficSources"][i] is None):
            suspicion_score+=1
        else:    
            trafficTracker+=resultDict["TrafficSources"][i]
            if trafficTracker==0:
                suspicion_score +=1
    
    if len(resultDict["SearchTerms"]) <=20:
        suspicion_score+=1
        
    if suspicion_score >= 3:
        return True
    
    return False