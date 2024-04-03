import scrapy
import socket
from OpenSSL import SSL
from twisted.internet.error import DNSLookupError, TCPTimedOutError
from scrapy.spidermiddlewares.httperror import HttpError
from OpenSSL.SSL import Error as SSLError
from urllib.parse import urlparse
import logging

# # Disable all logging
logging.disable(logging.CRITICAL)

class SSLSpider(scrapy.Spider):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    name = 'ssl_spider'
    ssl_certified = False
    valid_ssl = False
    issuer_common_name = None

    def start_requests(self):
        # Get the URL from the command-line argument
        url = getattr(self, 'url', None)
        if url is None or url.strip() == '':
            print('Please enter a valid URL.')
            return

        # Check if the URL has a scheme, if not, try with https:// first
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = 'https://' + url

        # Use the URL directly in the request, with dont_redirect set to True
        yield scrapy.Request(url,
                            self.parse,
                            errback=self.handle_error,
                            meta={'dont_redirect': True},
                            headers=self.headers)  # Pass headers here
    def handle_error(self, failure):
        # If HTTP request fails, try with HTTPS
        url = failure.request.url
        if url.startswith('http://'):
            fallback_url = url.replace('http://', 'https://', 1)
            yield scrapy.Request(fallback_url, self.parse, errback=self.handle_final_error)
        else:
            self.handle_final_error(failure)

    def handle_final_error(self, failure):
        # Handle final errors after all retry attempts
        if isinstance(failure.value, HttpError):
            # HTTP error (e.g., 404, 500, etc.)
            print(f'{failure.request.url} is a valid HTTP URL but returned an error: {failure.value.response.status}')
        elif isinstance(failure.value, DNSLookupError):
            # DNS lookup failed
            print(f'{failure.request.url} is not a valid URL.')
        elif isinstance(failure.value, SSLError):
            # SSL error, including expired certificates
            print(f'This URL is not safe: {failure.request.url}')
        else:
            # Other errors
            print(f'Failed to retrieve {failure.request.url}. Please enter a valid URL.')


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

                ssl_certified = True

                # Check if the issuer's common name is similar to the hostname
                if hostname.endswith(issuer_common_name) or issuer_common_name.endswith(hostname):
                    # print(f"{response.url} is SSL certified, but the CA is likely self-signed: {issuer_common_name}")
                    valid_ssl = False
                else:
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
                        'Google',
                        'GTS'
                    ]
                    # Check if the issuer is in the list of trusted CAs
                    if any(trusted_ca in issuer_common_name for trusted_ca in trusted_cas):
                        # print(f"{response.url} is SSL certified with a valid CA: {issuer_common_name}")
                        valid_ssl = True
                    else:
                        # print(f"{response.url} is SSL certified, but the CA '{issuer_common_name}' is not in the list of trusted CAs.")
                        valid_ssl = False

                # Close the connection
                connection.shutdown()
                connection.close()

            except SSL.Error:
                # print(f"{response.url} is not SSL certified.")
                ssl_certified = False
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            # print(f"{response.url} is not a HTTPS URL.")
            ssl_certified = False
        print(f"SSL Certified: {ssl_certified}")
        print(f"SSL Validity: {valid_ssl}")
        if not valid_ssl:
            issuer_common_name = None
        print(f"Issued Certificate by: {issuer_common_name}")
            