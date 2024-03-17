from flask import Flask, jsonify, request
from flask_cors import CORS
from database_analysis import *
from domain_analysis import *

app = Flask(__name__)
CORS(app)

stop_scan = False

def check_abort_scan():
    global stop_scan
    return stop_scan

# Function to perform domain analysis
def checklist_scan(domain):
    is_malicious = False
    global stop_scan
    stop_scan = False
    
    if domain:
        database_result = None
        domain_result = None
        phishing_checklist_dict = {}
        
        while(database_result == None and domain_result == None):
            if (stop_scan):
                break
            
            # # Perform domain analysis
            if (not domain_result):
                domain_result = virustotal(domain)
            
            # # Perform database analysis
            if (not database_result):
                database_result = database_analysis(domain)
                phishing_checklist_dict["Database"] = database_result 
                is_malicious = database_result
                print(is_malicious)
                
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
    return jsonify({'results': results}), 200

# Route for scanning a single domain
@app.route('/scan', methods=['POST', 'OPTIONS'])
def scan_domain():
    if request.method == 'OPTIONS':
        return '', 204  # Respond with no content for OPTIONS requests
    data = request.get_json()
    received_domain = data.get('domain', None)
    is_malicious = checklist_scan(received_domain)
    return jsonify({'results': is_malicious}), 200

# Route for aborting the scan
@app.route('/abort-scan', methods=['POST', 'OPTIONS'])
def abort_scan():
    global stop_scan
    stop_scan = True
    return jsonify({'message': 'Stop signal received'}), 200

if __name__ == '__main__':
    app.run(debug=True)
