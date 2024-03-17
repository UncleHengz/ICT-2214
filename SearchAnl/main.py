from search import check_site_google
from safebrowsing import check_url_safe
from safebrowsing import list_Maker_safeBrowsing
from simweb import similarGet
from simweb import filteredDict
from simweb import pretty_print_dict

def assess_phishing_risk(url):
    # Assuming you've set your API key globally or within the safebrowsing.py module
    api_key = "AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU"
    
    suspicion_score = 0
    
    # Use search.py to check if the site is indexed by Google
    is_indexed, search_message = check_site_google(url)
    if not is_indexed:
        suspicion_score += 1

    # Use safebrowsing.py to check against Google's Safe Browsing API
    safe, safe_message = check_url_safe(api_key, url)
    if  safe == False :
        suspicion_score += 5  # Adjust the score based on your risk assessment
    
    # Use SIMWEB.py to get site metrics
    site_metrics = similarGet(url)
    #thinking of logic to assess site_metrics and adjust suspicion_score

    # Combine results to make a final assessment
    if suspicion_score >= 5:  # Threshold is arbitrary; adjust based on your criteria
        return True, "High risk of phishing"
    else:
        return False, "Low risk of phishing"

if __name__ == '__main__':
    url_to_check = "https://testsafebrowsing.appspot.com/s/phishing.html"  # Replace with the URL you want to assess
    risk, message = assess_phishing_risk(url_to_check)
    print(f"Risk Assessment for {url_to_check}: {message}")
