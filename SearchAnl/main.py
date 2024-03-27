from search import check_site_google
from safebrowsing import check_url_safe
from simweb import similarGet
from simweb import filteredDict
from simweb import SussyChecker
def assess_phishing_risk(url):
    api_key = "AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU"
    
    suspicion_score = 0
    
    # Use search.py to check if the site is indexed by Google
    is_indexed, num_results = check_site_google(url)
    if num_results<=50: #not sure what should i adjust this number to 
        suspicion_score += 1

    # Use safebrowsing.py to check against Google's Safe Browsing API
    safe, safe_message = check_url_safe(api_key, url)
    if  safe == False :
        suspicion_score += 5  # Adjust the score based on your risk assessment
    
    # Use SIMWEB.py to get site metrics
    site_metrics = similarGet(url)
    suspicion_score+=SussyChecker(filteredDict(site_metrics))
     

    # Combine results to make a final assessment
    if suspicion_score >= 5: 
        return True, "High risk of phishing",suspicion_score
    else:
        return False, "Low risk of phishing", suspicion_score

if __name__ == '__main__':
    url_to_check = "https://testsafebrowsing.appspot.com/s/phishing.html"  # Replace with the URL to assess
    # if test with "http://fb.com" can see it is low risk , as it refers to facebook
    risk, message,suspicion_score = assess_phishing_risk(url_to_check)
    print(f"Risk Assessment for {url_to_check}: {message} with suspicion score of {suspicion_score}")
