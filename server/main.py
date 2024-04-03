from flask import Flask, jsonify, request
from flask_cors import CORS
from database_analysis import database_scan
from domain_analysis import virustotal
from search_engine.search_analysis import assess_phishing_risk
from generate_file import create_pdf_report
from generative_ai import gen_ai
import os
import subprocess
import requests
import base64
from urllib.parse import urlparse


app = Flask(__name__)
CORS(app)

stop_scan = False
domain_result_details = {}
database_result_details = {}
ssl_result_details = {}
content_result_details = {}
search_result_details = {}


def check_abort_scan():
    global stop_scan
    return stop_scan

# Function that assigns a score to each result if true and perform total calculation
def malicious_calculation(phishing_checklist):
    scores = {
        'database_result': 4,  
        'domain_result': 2,
        'cert_result': 1,
        'content_result': 0.5,
        'search_result': 2
    }
    
    total_score = 0
    
    for key, value in phishing_checklist.items():
        if value:  # If the analysis result is True (indicating malicious)
            total_score += scores[key]

    if total_score >= 4.5:
        return True # malicious 
    else:
        return False # not malicious

def ssl_analysis(domain):
    command = ["scrapy", "crawl", "ssl_spider", "-a", f"url={domain}"]
    
    try:
        result = subprocess.run(command, cwd="sslchecker", capture_output=True, text=True, check=True)
        # Access stdout and stderr
        stdout = result.stdout
        # Split the output into lines
        lines = stdout.split('\n')
        print(lines)
        if len(lines) >= 3:
            # Extract values from each line
            ssl_cert = lines[0].split(': ')[1]
            ssl_authorised_ca = lines[1].split(': ')[1]
            issued_by = lines[2].split(': ')[1]
        else:
            ssl_cert = lines[0].split(': ')[1]
            ssl_authorised_ca = None
            issued_by = None
        result_details = {
            "SSL": ssl_cert,
            "Authorised CA": ssl_authorised_ca,
            "Issued By": issued_by 
        }
        
        if ssl_authorised_ca is None:
            return True, result_details
        
        if ssl_cert is True and ssl_authorised_ca is True:
            return False, result_details
        else:
            return True, result_details
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        
def content_analysis(domain_path):
    command = ['python3', 'spell_check_spider.py', domain_path]
    try:
        result = subprocess.run(command, cwd="spellcheck_spider/spellcheck_spider/spiders", capture_output=True, text=True, check=True)
        stdout = result.stdout
        # Split the output into lines
        lines = stdout.split('\n')
        # Extract values from each line
        errors = (lines[0].split(': ')[1]).strip("[]").split(", ")
        error_pct = lines[1].split(': ')[1]
        
        total_errors = len(errors)
        query = f"This website is {domain_path} and has a total of {total_errors} errors, which include {errors}. \
        This accounts for {error_pct}% of the words being misspelled. Be realistic and objective. \
        Do you think this website is suspicious/phishing? Use only 2 sentences. First sentence to state Yes or No. Second sentence to state the reason"
        response = gen_ai(query)
        
        sentence = response.text
        # Find the index of the period to split the sentence
        period_index = sentence.find('.')
        # Split the sentence into two parts based on the period
        malicious_part = sentence[:period_index].strip()  # Include the period and remove leading/trailing whitespaces
        description_part = sentence[period_index + 1:].strip()  # Exclude the period and remove leading/trailing whitespaces

        result_details = {
            "Total Errors": total_errors,
            "Percentage Wrongly Spelled": error_pct,
            "Reason": description_part
        }
            
        if "Yes" in malicious_part:
            return True, result_details
        elif "No" in malicious_part:
            return False, result_details
        else:
            return None, ""
        
    except subprocess.CalledProcessError as e:
        print("Subprocess error:", e.stderr)
    
# Function to perform domain analysis
def checklist_scan(url):
    is_malicious = False
    global stop_scan, domain_result_details, database_result_details, ssl_result_details, search_result_details, content_result_details
    stop_scan = False
    
    if isinstance(url, bytes):
        url = url.decode('utf-8')  # or 'utf-8-sig' depending on your encoding
    
    if url:
        if url.startswith("http://") or url.startswith("https://"):
            parsed_url = urlparse(url)
            # Filter to retrieve the domain name and path
            domain = parsed_url.hostname
            path = parsed_url.path
            
            # Combine eg. www.google.com
            domain_path = domain + path
        else:
            domain_path = url
            domain = url

        phishing_checklist = {
            'database_result': None,
            'domain_result': None,
            'cert_result': None,
            'content_result': None,
            'search_result': None
        }
        
        if check_abort_scan():
            return None

        # Perform domain analysis
        print("start domain analysis..")
        result, domain_result_details = virustotal(domain)
        domain_result_details["Result"] = result
        if result is None or check_abort_scan():
            print("Domain analysis stopped")
            return None
        phishing_checklist['domain_result'] = result

        # Perform database analysis
        print("start database analysis..")
        result, database_result_details = database_scan(domain_path)
        database_result_details["Result"] = result
        if result is None or check_abort_scan():
            print("Database analysis stopped")
            return None
        phishing_checklist['database_result'] = result

        # Perform SSL Cert analysis
        print("start SSL analysis..")
        result, ssl_result_details = ssl_analysis(domain)
        ssl_result_details["Result"] = result
        if result is None or check_abort_scan():
            print("SSL analysis stopped")
            return None
        phishing_checklist['cert_result'] = result

        # Perform Content analysis
        print("start content analysis..")
        result, content_result_details = content_analysis(domain_path)
        content_result_details["Result"] = result
        if result is None or check_abort_scan():
            print("Content analysis stopped")
            return None
        phishing_checklist['content_result'] = result
        
        # Perform Search Engine analysis
        print("start search analysis..")
        result, search_result_details = assess_phishing_risk(domain_path)
        search_result_details["Result"] = result
        if result is None or check_abort_scan():
            print("Search Engine analysis stopped")
            return None
        phishing_checklist['search_result'] = result
                
        is_malicious = malicious_calculation(phishing_checklist)   
        
    return is_malicious

# Route for scanning all domains
@app.route('/scan-all', methods=['POST', 'OPTIONS'])
def scan_all_domains():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    global stop_scan
    stop_scan = False
    
    data = request.get_json()
    received_domains = data.get('domains', [])
    results = {}
    for domain in received_domains:
        if (check_abort_scan()):
            break
        is_malicious = checklist_scan(domain)
        results[domain] = is_malicious
        print(results[domain])
    return jsonify({'results': results}), 200

# Route for scanning a single domain
@app.route('/scan', methods=['POST', 'OPTIONS'])
def scan_domain():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    data = request.get_json()
    received_link = data.get('link', None)
    
    if received_link is None:
        # Return error response
        error_message = "Error occurred during scan."
        return jsonify({'error': error_message}), 500

    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    #            'Connection': 'keep-alive'}
    # # Check if the URL is reachable
    # print(received_link)
    # try:
    #     response = requests.head(received_link, headers=headers)
    #     response.raise_for_status()  # Raise an error for non-2xx status codes
    # except requests.exceptions.RequestException as e:
    #     # Return error response if the URL is not reachable
    #     print(e)
    #     error_message = f"Error occurred while reaching the link: {e}"
    #     return jsonify({'error': error_message}), 404
    
    # Perform the scan
    is_malicious = checklist_scan(received_link)
    
    if is_malicious is None:
        # Return error response
        error_message = "Error occurred during scan."
        return jsonify({'error': error_message}), 500
    
    return jsonify({'results': is_malicious}), 200

# Route for aborting the scan
@app.route('/abort-scan', methods=['POST', 'OPTIONS'])
def abort_scan():
    global stop_scan
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    stop_scan = True
    return jsonify({'message': 'Stop signal received'}), 200

# Route for aborting the scan
@app.route('/download', methods=['POST', 'OPTIONS'])
def download_report():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    try:
        if domain_result_details is not None:
            all_details = {
                "domain": domain_result_details,
                "database": database_result_details,
                "ssl": ssl_result_details,
                "content": content_result_details,
                "search": search_result_details
            }
            domain = request.json.get('domain')
            pdf_content = create_pdf_report(domain, all_details)
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            response = jsonify({'pdf_base64': pdf_base64})
            return response
        else:
            print("Download is unable to get details")
            return response,500
    except Exception as e:
        print("Error at download:", e)
        response = jsonify({'error': str(e)})
        return response, 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
