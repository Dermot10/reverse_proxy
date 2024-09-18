from flask import Flask
from flask import jsonify, request
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from severless_reverse_proxy.rp_routing import ReverseProxy

app = Flask(__name__)

# Initialize the reverse proxy
proxy = ReverseProxy()


@app.route('/proxy/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_proxy(path):
    """Flask route to handle proxying requests"""

    # Dummy event to test reverse proxy
    event = {
        'httpMethod': request.method,
        'path': '/' + path,
        'body': request.get_data(as_text=True) if request.method in ['POST', 'PUT'] else None,
        'headers': dict(request.headers)
    }

    # Pass the event to the reverse proxy and get the response
    proxy_response = proxy.extract_request_data(event)

    # Flask will use the response data returned from the proxy
    return jsonify(json.loads(proxy_response['body'])), proxy_response['statusCode']


if __name__ == '__main__':
    app.run(port=5001)
