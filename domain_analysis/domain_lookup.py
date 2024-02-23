import requests
import dns.resolver

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

    result = {
        'Domain': data['name'],
        'Status': data['status'],
        'Name Servers': data['nameserver'],
        'IPs': data['ips'],
        'Created': data['created'],
        'Changed': data['changed'],
        'Expires': data['expires'],
        'Registrar': data['registrar']['name'] if 'registrar' in data else None,
        'Contacts': {
            'Owner': data['contacts']['owner'][0] if 'owner' in data['contacts'] and data['contacts']['owner'] else None,
            'Admin': data['contacts']['admin'][0] if 'admin' in data['contacts'] and data['contacts']['admin'] else None,
            'Tech': data['contacts']['tech'][0] if 'tech' in data['contacts'] and data['contacts']['tech'] else None
        }
    }

    return result

# Example Usage
domain = "singaporetech.edu.sg"
dns_lookup(domain)

for key, value in whois(domain).items():
    if isinstance(value, dict):
        print(f"{key}:")
        for sub_key, sub_value in value.items():
            print(f"  {sub_key}: {sub_value}")
    else:
        print(f"{key}: {value}")