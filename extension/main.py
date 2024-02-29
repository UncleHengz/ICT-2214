from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/scan-all', methods=['POST'])
def scan_all_domains():
    if request.method == 'POST':
        data = request.get_json()
        received_domains = data.get('domains', [])

        print("Scanned Domains:")
        for domain in received_domains:
            print(domain)

        return jsonify({'message': 'Domains processed successfully'})

@app.route('/scan', methods=['POST'])
def scan_domain():
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        received_domain = data.get('domain', None)

        if received_domain:
            print("Scanned Domain:", received_domain)
            
            # Perform scanning or processing for the single domain
            # For illustration purposes, assuming it's safe (modify as needed)
            status = False
            for i in range (1000000000):
                if (i % 100000000 == 0):
                    print("testing intervals");
            status = True

            # Returning a JSON response with a 'status' key
            return jsonify({'status': status}), 200
        else:
            return jsonify({'error': 'No domain provided in the request'}), 400

if __name__ == '__main__':
    app.run(debug=True)
