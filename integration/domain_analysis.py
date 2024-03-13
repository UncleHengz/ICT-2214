import requests
#import dns.resolver
from datetime import datetime
from urllib.parse import urlparse
import re

### Just putting this here, might be useful for the plugin implementation part
# def get_domain_from_url(url):
#     parsed_url = urlparse(url)
#     return parsed_url.netloc

# # Example usage:
# url = "https://singaporetech.edu.sg"
# test = get_domain_from_url(url)
# print("Domain:", test)

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
        return None  # Unable to determine suspiciousness
    if age < 366 or update_age < 30:
        return 3  # Very suspicious
    elif age < 732 or update_age < 15:
        return 2  # Moderately suspicious
    else:
        return 1  # Less suspicious

# def whois(domain):
    url = "https://zozor54-whois-lookup-v1.p.rapidapi.com/"
    querystring = {
        "domain": domain,
        "format": "json",
        "_forceRefresh": "0"
    }
    headers = {
        "X-RapidAPI-Key": "e3da8e7390msha58253180e1c0d6p19545fjsn2f1f4b97e2cd",
        "X-RapidAPI-Host": "zozor54-whois-lookup-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    if 'exception' in data and data['exception'] is not None:
        return f"An error occurred: {data['exception']}"
    
    created_date = data['created']
    created_age = (datetime.utcnow() - datetime.strptime(created_date, "%Y-%m-%d %H:%M:%S")).days

    updated_date = data['changed']
    update_age = (datetime.utcnow() - datetime.strptime(updated_date, "%Y-%m-%d %H:%M:%S")).days

    suspiciousness = determine_suspiciousness(created_age, update_age)

    result = {
        'Domain': data['name'],
        'Status': data['status'],
        'Name Servers': data['nameserver'],
        'IPs': data['ips'],
        'Created': created_date,
        'Changed': updated_date,
        'Expires': data['expires'],
        'Registrar': data['registrar']['name'] if 'registrar' in data else None,
        'Contacts': {
            'Owner': data['contacts']['owner'][0] if 'owner' in data['contacts'] and data['contacts']['owner'] else None,
            'Admin': data['contacts']['admin'][0] if 'admin' in data['contacts'] and data['contacts']['admin'] else None,
            'Tech': data['contacts']['tech'][0] if 'tech' in data['contacts'] and data['contacts']['tech'] else None
        },
        'Age (in days)': created_age,
        'Last Updated (in days)': update_age,
        'Suspiciousness': suspiciousness
    }

    return result

def calculate_suspiciousness(analysis_stats):
    weights = {
        "harmless": 0,
        "malicious": 3,
        "suspicious": 2,
        "undetected": 1,
        "timeout": 0
    }

    return sum(analysis_stats[category] * weights[category] for category in analysis_stats)

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
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {"x-apikey": "82a2d1a9192167470ad718102b312c5745a9b14ea17c3e0468b03d616ad21dc3"}

    response = requests.get(url, headers=headers)
    data = response.json()['data']

    analysis = data['attributes']['last_analysis_stats']
    score = calculate_suspiciousness(analysis)

    whois_data = parse_whois(data['attributes']['whois'])
    whois_dates = parse_whois_dates(whois_data)

    age = None
    update_age = None

    for key, value in whois_dates.items():
        for pattern in creation_patterns:
            if re.match(pattern, key):
                age = calculate_age(parse_date(value))
                created_date = parse_date(value)
                break
        for pattern in update_patterns:
            if re.match(pattern, key):
                update_age = calculate_update_age(parse_date(value), created_date)
                break

    suspiciousness = determine_suspiciousness(age, update_age)

    dns_records = group_dns_records(data['attributes']['last_dns_records'])

    result = {
        'Domain': data['id'],
        'Type': data['type'],
        'DNS Records': dns_records,
        'Whois Dates': whois_dates,
        'Popularity': data['attributes']['popularity_ranks'],
        "Analysis Stats": data['attributes']['last_analysis_stats'],
        "Categories": data['attributes']['categories'],
        "Analysis Score": score,
        "Suspiciousness": suspiciousness
    }

    return result


# # Example Usage
# domain = "amaonz.xjijin.com.cn"

# for key, value in whois(domain).items():
#     if isinstance(value, dict):
#         print(f"{key}:")
#         for sub_key, sub_value in value.items():
#             print(f"  {sub_key}: {sub_value}")
#     else:
#         print(f"{key}: {value}")

# for key, value in virustotal(domain).items():
#     if isinstance(value, dict):
#         print(f"{key}:")
#         for sub_key, sub_value in value.items():
#             print(f"  {sub_key}: {sub_value}")
#     else:
#         print(f"{key}: {value}")