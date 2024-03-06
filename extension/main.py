from flask import Flask, jsonify, request
from flask_cors import CORS

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
        scan_result = False

        if received_domain and not abort_signal_received:
            print("Scanned Domain:", received_domain)

            for i in range(100000000):
                if abort_signal_received:
                    print("Scan aborted by user")
                    abort_signal_received = True
                    return jsonify({'scan_result': 'aborted'}), 200

                if i % 100000000 == 0:
                    print("Testing intervals")

            scan_result = True
            # Returning a JSON response with a 'status' key
            return jsonify({'scan_result': scan_result}), 200
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
