import requests
import dns.resolver
from datetime import datetime

def calculate_age(created_date):
    created_date = datetime.strptime(created_date, "%Y-%m-%d %H:%M:%SZ")
    current_date = datetime.utcnow()
    age = (current_date - created_date).days
    return age

def calculate_update_age(updated_date):
    updated_date = datetime.strptime(updated_date, "%Y-%m-%d %H:%M:%SZ")
    current_date = datetime.utcnow()
    age = (current_date - updated_date).days
    return age

def determine_suspiciousness(age, update_age):
    if age < 365 or update_age < 30:
        return 3  # Very suspicious
    elif age < 730 or update_age < 90:
        return 2  # Moderately suspicious
    else:
        return 1  # Less suspicious

def dns_lookup(domain):
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME', 'PTR', 'SRV', 'NAPTR', 'CAA']
    for record_type in record_types:
        try:
            result = dns.resolver.resolve(domain, record_type)
            output = [ex.to_text() for ex in result]
            print(f"{record_type} Record: {output}")
        except dns.resolver.NoAnswer:
            print(f"No {record_type} record found for {domain}")
            continue

def whois(domain):
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

# Example Usage
domain = "singaporetech.edu.sg"
#dns_lookup(domain)

for key, value in whois(domain).items():
    if isinstance(value, dict):
        print(f"{key}:")
        for sub_key, sub_value in value.items():
            print(f"  {sub_key}: {sub_value}")
    else:
        print(f"{key}: {value}")

# print(type(whois(domain)["Created"]))