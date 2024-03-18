import scrapy
import socket
from OpenSSL import SSL
import logging

# # Disable all logging
logging.disable(logging.CRITICAL)

class SSLSpider(scrapy.Spider):
    name = 'ssl_spider'

    def start_requests(self):
        # Get the URL from the command-line argument
        url = getattr(self, 'url', None)
        if url is not None:
            # Check if the URL starts with http:// or https://, if not, prepend https://
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Use the URL directly in the request
            yield scrapy.Request(url, self.parse)
        else:
            print('URL not provided. Use the -a option to specify the URL. Example: scrapy crawl ssl_spider -a url=https://www.example.com')

    def parse(self, response):
        # Check if the response is for an HTTPS request
        if response.url.startswith('https://'):
            try:
                # Extract the hostname from the URL
                hostname = response.url.split('://')[1].split('/')[0]

                # Establish an SSL connection and get the certificate
                context = SSL.Context(SSL.TLSv1_2_METHOD)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                connection = SSL.Connection(context, sock)
                connection.connect((hostname, 443))
                connection.do_handshake()
                cert = connection.get_peer_certificate()
                issuer = cert.get_issuer()

                # Get the issuer's common name
                issuer_common_name = issuer.commonName

                # List of trusted CAs
                trusted_cas = [
    'DigiCert',
    'Let\'s Encrypt',
    'GlobalSign',
    'Comodo',
    'GoDaddy',
    'Thawte',
    'GeoTrust',
    'RapidSSL',
    'Sectigo',
    'Entrust',
    'Symantec',
    'Verisign',
    'StartCom',
    'QuoVadis',
    'Trustwave',
    'Network Solutions',
    'SwissSign',
    'IdenTrust',
    'Amazon',
    'Microsoft',
    'Google'
]
                # Check if the issuer is in the list of trusted CAs
                if any(trusted_ca in issuer_common_name for trusted_ca in trusted_cas):
                    print(f"{response.url} is SSL certified with a valid CA: {issuer_common_name}")
                else:
                    print(f"{response.url} is SSL certified, but the CA '{issuer_common_name}' is not in the list of trusted CAs.")

                # Close the connection
                connection.shutdown()
                connection.close()

            except SSL.Error:
                print(f"{response.url} is not SSL certified.")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print(f"{response.url} is not a HTTPS URL.")