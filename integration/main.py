from flask import Flask, jsonify, request
from flask_cors import CORS
from database_analysis import database_scan
from domain_analysis import virustotal
from search_engine.search_analysis import assess_phishing_risk
from generate_file import create_pdf_report
import os
import subprocess
import requests
import base64

app = Flask(__name__)
CORS(app)

stop_scan = False
domain_result_details = {}
database_details = {}
ssl_result_details = {}
search_result_details = {}
content_result_details = {}

def check_abort_scan():
    global stop_scan
    return stop_scan

# Function to check if a domain exists
def check_domain_exists(domain):
    try:
        response = requests.head("http://" + domain)
        return response.status_code < 400
    except requests.exceptions.RequestException:
        return False

# Function that assigns a score to each result if true and perform total calculation
def malicious_calculation(phishing_checklist):
    scores = {
        'database_result': 3,  
        'domain_result': 2,
        'cert_result': 2,
        'content_result': 2,
        'search_result': 1
    }
    
    total_score = 0
    
    for key, value in phishing_checklist.items():
        if value:  # If the analysis result is True (indicating malicious)
            total_score += scores[key]

    if total_score >= 5:
        return True # malicious 
    else:
        return False # not malicious

def ssl_analysis(domain):
    command = ["scrapy", "crawl", "ssl_spider", "-a", f"url={domain}"]
    
    try:
        result = subprocess.run(command, cwd="sslchecker", capture_output=True, text=True, check=True)
        # Access stdout and stderr
        stdout = result.stdout
        # print(f"Standard Output:\n", stdout)
        
        # Split the output into lines
        lines = stdout.split('\n')
        # Extract values from each line
        ssl_cert = lines[0].split(': ')[1]
        ssl_authorised_ca = lines[1].split(': ')[1]
        issued_by = lines[2].split(': ')[1]
        
        result_details = {
            "SSL": ssl_cert,
            "Authorised CA": ssl_authorised_ca,
            "Issued By": issued_by 
        }
        
        if ssl_cert and ssl_authorised_ca:
            return True, result_details
        else:
            return False, result_details
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    
# Function to perform domain analysis
def checklist_scan(domain):
    is_malicious = False
    global stop_scan, domain_result_details, database_details, ssl_result_details, search_result_details
    stop_scan = False
    
    if domain:
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
        result, domain_result_details = virustotal(domain)
        if result is None or check_abort_scan():
            print("Domain analysis stopped")
            return None
        phishing_checklist['domain_result'] = result

        # Perform database analysis
        result, database_details = database_scan(domain)
        if result is None or check_abort_scan():
            print("Database analysis stopped")
            return None
        phishing_checklist['database_result'] = result

        # Perform SSL Cert analysis
        result, ssl_result_details = ssl_analysis(domain)
        if result is None or check_abort_scan():
            print("SSL analysis stopped")
            return None
        phishing_checklist['cert_result'] = result

        # # Perform Content analysis
        result = False
        # result = content_analysis(domain)
        # if result is None or check_abort_scan():
        #     return None
        # phishing_checklist['content_result'] = result
        
        # Perform Search Engine analysis
        result, search_result_details = assess_phishing_risk(domain)
        if result is None or check_abort_scan():
            print("Search Engine analysis stopped")
            return None
        phishing_checklist['search_engine'] = result
                
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
    received_domain = data.get('domain', None)

    # Check if domain exists
    if not check_domain_exists(received_domain):
        error_message = "Domain does not exist or cannot be reached."
        return jsonify({'error': error_message}), 404

    # Perform the scan
    is_malicious = checklist_scan(received_domain)
    
    if is_malicious is None:
        # Return error response
        error_message = "Error occurred during domain scan."
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
                "database": database_details,
                "ssl": ssl_result_details,
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
    app.run(debug=True)
