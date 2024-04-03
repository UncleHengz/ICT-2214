import requests
from datetime import datetime
from urllib.parse import urlparse
import re

def get_domain_from_url(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == '':
        domain_parts = parsed_url.path.split('.')
        index = len(domain_parts)
        end = domain_parts[index - 1].split('/')
        if domain_parts[0].startswith("www"):
            domain = '.'.join(domain_parts[1:index-1]) + '.' + end[0]
            return domain
        else:
            domain = '.'.join(domain_parts[0:index-1]) + '.' + end[0]
            return domain
    
    domain_parts = parsed_url.netloc.split('.')
    if domain_parts[0].startswith("www"):
        return '.'.join(domain_parts[1:])
    else:
        domain = '.'.join(domain_parts[0:])
        return domain

# Regular expression patterns for matching creation and update dates
creation_patterns = [r'(?i)(create[d]?[ ]?date|creat[ion]?)[ ]?[:]?[\s\-/:]*']
update_patterns = [r'(?i)(update[d]?[ ]?date|modif[ication]?)[ ]?[:]?[\s\-/:]*']

def calculate_age(created_date):
    created_date = datetime.fromisoformat(created_date).date()  # Extract only date part
    current_date = datetime.utcnow().date()  # Extract only date part
    age = (current_date - created_date).days
    return age

def calculate_update_age(updated_date, created_date):
    updated_date = datetime.fromisoformat(updated_date).date()  # Extract only date part
    created_date = datetime.fromisoformat(created_date).date()  # Extract only date part
    age = (updated_date - created_date).days
    return age

def determine_suspiciousness(age, update_age):
    if age is None or update_age is None:
        return 0, "Unable to determine"  # Unable to determine suspiciousness
    if age < 366 or update_age < 30:
        return 3, "Very suspicious"  # Very suspicious
    elif age < 732 or update_age < 15:
        return 2, "Moderately suspicious"  # Moderately suspicious
    else:
        return 1, "Less suspicious"  # Less suspicious

def calculate_suspiciousness(analysis_stats):
    weights = {
        "harmless": 0,
        "malicious": 3,
        "suspicious": 2,
        "undetected": 1,
        "timeout": 0
    }

    if analysis_stats is None:
        return 0

    return sum(analysis_stats[category] * weights[category] for category in analysis_stats)

def categorize_threat(categories):
    threat_keywords = ['phish', 'fraud', 'scam', 'malware', 'ransomware', 'spyware', 'illegal', 'susp']  # Add more keywords as needed
    for category in categories.values():
        for keyword in threat_keywords:
            if re.search(keyword, category, re.IGNORECASE):
                return 100  # Very suspicious
    return 0  # No threat detected

def group_dns_records(last_dns_records):
    grouped_records = {}
    
    for record in last_dns_records:
        record_type = record.pop('type')
        if record_type in grouped_records:
            grouped_records[record_type].append(record)
        else:
            grouped_records[record_type] = [record]
    
    return grouped_records

def parse_whois(whois_data):
    whois_info = {}
    lines = whois_data.split('\n')
    for line in lines:
        if line.strip():  # Check if line is not empty
            parts = re.split(r':\s*', line, maxsplit=1)
            if len(parts) == 2:
                key, value = parts
                key = key.strip().replace(' ', '_')  # Replace spaces with underscores
                value = value.strip()
                if key in whois_info:
                    # If the key already exists, convert the value to a list
                    if isinstance(whois_info[key], list):
                        whois_info[key].append(value)
                    else:
                        # Convert the existing value to a list and append the new value
                        whois_info[key] = [whois_info[key], value]
                else:
                    whois_info[key] = value
            else:
                # Handle lines that don't have the format "key: value"
                # For now, you can just ignore these lines
                pass
    return whois_info

def parse_date(date_str):
    try:
        # Attempt to parse the date string in various formats
        return datetime.strptime(date_str, '%d-%b-%Y %H:%M:%S').isoformat()
    except ValueError:
        pass

    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').isoformat()
    except ValueError:
        pass

    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z').isoformat()
    except ValueError:
        pass

    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ').isoformat()
    except ValueError:
        pass

    # If the date format is not recognized, return the original string
    return date_str

def parse_whois_dates(whois_data):
    dates = {}
    date_variations = ['creat', 'update', 'modif', 'expir']

    for key, value in whois_data.items():
        key_lower = key.lower()
        matched_variation = None
        for variation in date_variations:
            pattern = rf'.*{variation}[\s\-/:]*'
            if re.match(pattern, key_lower, re.IGNORECASE):
                matched_variation = variation
                break

        if matched_variation:
            # Ignore the front part
            start_index = key_lower.find(matched_variation)
            original_key = key[start_index:]

            # Strip underscores
            original_key = original_key.replace('_', ' ')

            if isinstance(value, list):
                # Convert list to string and split it into individual date strings
                date_strings = ' '.join(value).split()
                # Keep only the first date if there are multiple dates
                date_string = date_strings[0]
            else:
                date_string = value

            # Convert the date string to a standard format
            parsed_date = parse_date(date_string)
            dates[original_key] = parsed_date

    return dates

def virustotal(domain):
    domain = get_domain_from_url(domain)

    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {"x-apikey": "82a2d1a9192167470ad718102b312c5745a9b14ea17c3e0468b03d616ad21dc3"}

    response = requests.get(url, headers=headers)

    # Initialize Malicious (boolean)
    malicious = False

    if 'error' in response.json():
        result = {'malicious': malicious}
        return f"An error occurred: {response.json()['error']['message']}", result
    
    else:
        data = response.json()['data']

        analysis = data['attributes']['last_analysis_stats']

        if 'whois' not in data['attributes']:
            result = {'malicious': malicious}
            return "Site does not exist" , result

        whois_data = parse_whois(data['attributes']['whois'])
        whois_dates = parse_whois_dates(whois_data)

        categories = data['attributes']['categories']

        age = None
        update_age = None

        for key, value in whois_dates.items():
            pattern_matched = False  # Flag to track if any pattern matched
            for pattern in creation_patterns:
                if re.match(pattern, key):
                    age = calculate_age(parse_date(value))
                    created_date = parse_date(value)
                    pattern_matched = True
                    break
            if not pattern_matched:  # If no pattern matched, break
                break
            
            pattern_matched = False  # Reset flag for the next loop
            
            for pattern in update_patterns:
                if re.match(pattern, key):
                    update_age = calculate_update_age(parse_date(value), created_date)
                    pattern_matched = True
                    break
            if not pattern_matched:  # If no pattern matched, break
                break

        age_sus, age_result = determine_suspiciousness(age, update_age)
        analysis_sus = calculate_suspiciousness(analysis)
        cat_sus = categorize_threat(categories)

        suspiciousness = age_sus + analysis_sus + cat_sus
        if suspiciousness >= 100:
            malicious = True

        dns_records = group_dns_records(data['attributes']['last_dns_records'])

        # result = {
        #     'Domain': data['id'],
        #     'Type': data['type'],
        #     'DNS Records': dns_records,
        #     'Whois Dates': whois_dates,
        #     'Popularity': data['attributes']['popularity_ranks'],
        #     "Analysis Stats": data['attributes']['last_analysis_stats'],
        #     "Categories": categories,
        #     "Suspiciousness": suspiciousness,
        #     "Malicious": malicious
        # }
        
        if cat_sus == 0:
            cat_result = False
        else:
            cat_result = True
        
        result = {
            "Age": age_result,
            "Anti-Virus Score": analysis_sus,
            "Category": cat_result
        }
        

        return malicious, result