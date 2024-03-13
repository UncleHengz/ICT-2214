from flask import Flask, jsonify, request
from flask_cors import CORS
from domain_analysis import *
from database_analysis import *

app = Flask(__name__)
CORS(app)

# Flag to check if an abort signal has been received
abort_signal_received = False

@app.route('/scan-all', methods=['POST'])
def scan_all_domains():
    if request.method == 'POST':
        data = request.get_json()
        received_domains = data.get('domains', [])

        print("Scanned Domains:")
        for domain in received_domains:
            print(domain)

        return jsonify({'message': 'Domains processed successfully'})

@app.route('/scan', methods=['OPTIONS', 'POST'])
def scan_domain():
    global abort_signal_received
    if request.method == 'OPTIONS':
        # Handle the preflight request
        return '', 204

    if request.method == 'POST':
        data = request.get_json()
        print(data)
        received_domain = data.get('domain', None)
        
        abort_signal_received = False
        is_malicious = False

        if received_domain and not abort_signal_received:
            print("Scanned Domain:", received_domain)

            database_result = None
            domain_result = None
            phishing_checklist_dict = {}
            
            while(database_result == None and domain_result == None):
                if abort_signal_received:
                    print("Scan aborted by user")
                    abort_signal_received = True
                    return jsonify({'scan_result': 'aborted'}), 200
                
                # # Perform domain analysis
                if (not domain_result):
                    domain_result = virustotal(received_domain)
                
                # # Perform database analysis
                if (not database_result):
                    database_result = database_analysis(received_domain)
                    phishing_checklist_dict["Database"] = database_result 
                    is_malicious = database_result
                    print(is_malicious)
                    
            # Returning a JSON response with a 'status' key
            return jsonify({'scan_result': is_malicious}), 200
        else:
            return jsonify({'error': 'No domain provided in the request'}), 400


@app.route('/abort-scan', methods=['OPTIONS', 'POST'])
def abort_scan():
    if request.method == 'OPTIONS':
        # Handle the preflight request
        return '', 204

    global abort_signal_received
    # Set the abort signal flag to True
    abort_signal_received = True
    return jsonify({'scan_result': 'abort signal received'}), 200

	
if __name__ == '__main__':
    app.run(debug=True)
