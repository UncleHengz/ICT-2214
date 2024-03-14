import requests

def check_site_google(url):
    api_key = "AIzaSyDJmKncAKqwTofjx3JhdhhVGcQK0eZ3yrU"  # Directly using the API key
    cse_id = "a6d5af5008e9e4d57"  # Direct use of the CSE ID

    query = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={url}"

    try:
        response = requests.get(query)
        response.raise_for_status()  # Raises an exception for 4XX and 5XX errors
        results = response.json()

        total_results = int(results.get("searchInformation", {}).get("totalResults", 0))
        if total_results > 0:
            return True, f"The site is indexed by Google. Total = {total_results} results found"
        else:
            return False, "The site is not indexed by Google."
    except requests.exceptions.RequestException as e:
        # Catch all requests exceptions
        return False, f"Request error occurred: {e}"

if __name__ == "__main__":
    url_to_check = "https://amaonz.xjijin.com.cn"
    is_indexed, message = check_site_google(url_to_check)
    print(message)
