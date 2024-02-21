from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

allowed_domains = []

@app.route('/api/domains', methods=['POST'])
def handle_domains():
    global allowed_domains

    if request.method == 'POST':
        data = request.get_json()
        received_domains = data.get('domains', [])

        # Update the allowed_domains list
        allowed_domains = received_domains
        print(allowed_domains)
        return jsonify({'message': 'Domains updated successfully'})

if __name__ == '__main__':
    app.run(debug=True)
