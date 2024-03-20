from flask import Flask, jsonify, request
from flask_cors import CORS
from database_analysis import database_scan
from domain_analysis import virustotal
from search_engine.search_analysis import assess_phishing_risk
import os
import subprocess

app = Flask(__name__)
CORS(app)

stop_scan = False

def check_abort_scan():
    global stop_scan
    return stop_scan

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
    os.chdir("sslchecker")
    command = ["scrapy", "crawl", "ssl_spider", "-a", f"url={domain}"]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # Access stdout and stderr
        stdout = result.stdout
        print(f"Standard Output:\n", stdout)
        
        # Split the output into lines
        lines = stdout.split('\n')
        # Extract values from each line
        ssl_cert = lines[0].split(': ')[1]
        ssl_authorised_ca = lines[1].split(': ')[1]
        issued_by = lines[2].split(': ')[1]
        
        if ssl_cert and ssl_authorised_ca:
            return True, issued_by
        else:
            return False, ""
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    
# Function to perform domain analysis
def checklist_scan(domain):
    is_malicious = False
    global stop_scan
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
        result = virustotal(domain)
        if result is None or check_abort_scan():
            print("Domain analysis stopped")
            return None
        phishing_checklist['domain_result'] = result

        # Perform database analysis
        result = database_scan(domain)
        if result is None or check_abort_scan():
            print("Database analysis stopped")
            return None
        phishing_checklist['database_result'] = result

        # Perform SSL Cert analysis
        result = ssl_analysis(domain)
        if result is None or check_abort_scan():
            print("SSL analysis stopped")
            return None
        phishing_checklist['cert_result'] = result

        # # Perform Content analysis
        # result = False
        # # result = content_analysis(domain)
        # if result is None or check_abort_scan():
        #     return None
        # phishing_checklist['content_result'] = result
        
        # Perform Search Engine analysis
        result = assess_phishing_risk(domain)
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
        return '', 204  # Respond with no content for OPTIONS requests
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
        return '', 204  # Respond with no content for OPTIONS requests
    data = request.get_json()
    received_domain = data.get('domain', None)
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
    stop_scan = True
    return jsonify({'message': 'Stop signal received'}), 200

if __name__ == '__main__':
    app.run(debug=True)
