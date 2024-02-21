import requests
import dns.resolver

def dns_lookup(domain):

    record_types = ['A', 'MX', 'TXT', 'NS', 'SOA']
    for record_type in record_types:
        result = dns.resolver.resolve(domain, record_type)
        # if dns.resolver.NoAnswer:
        #     print(f"No {record_type} record found for {domain}")
        #     continue
        output = []
        for ex in result:
            output.append(ex.to_text())
        print(f"{record_type} Record: {output}")
    
                
# def whois(domain):
#     url = "https://whois-lookup-service.p.rapidapi.com/v1/getwhois"
#     querystring = {"url": domain}
#     headers = {
#         "X-RapidAPI-Key": "e3da8e7390msha58253180e1c0d6p19545fjsn2f1f4b97e2cd",
#         "X-RapidAPI-Host": "whois-lookup-service.p.rapidapi.com"
#     }

#     response = requests.get(url, headers=headers, params=querystring)
#     data = response.json()

#     if data.get('error') is not None:
#         print(f"Error: {data['error']}")
#     else:
#         domain_data = data.get('data', {})
#         if domain_data:
#             for whois_server, details in domain_data.items():
#                 print("Domain Information:")
#                 for key, value in details.items():
#                     if isinstance(value, list):
#                         print(f"{key}:")
#                         for item in value:
#                             print(f"  - {item}")
#                     else:
#                         print(f"{key}: {value}")
#                 print()
#         else:
#             print("No WHOIS information available for this domain.")

# Example Usage
domain = "singaporetech.edu.sg"
# whois(domain)
dns_lookup(domain)