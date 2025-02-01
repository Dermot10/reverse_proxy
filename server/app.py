from flask import Flask
from flask import jsonify, request
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from serverless_reverse_proxy.local_reverse_proxy import LocalReverseProxy


app = Flask(__name__) 

# Initialize the reverse proxy
proxy = LocalReverseProxy()


@app.route('/proxy/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_proxy(path):
    """Flask route to handle proxying requests"""
    print(path)
    path_value = request.view_args['path']
    formatted_url = '/' + path_value

    request_data = {
        "method": request.method,
        "headers": dict(request.headers),
        "data": request.get_data().decode("utf-8"),
        "url": formatted_url
    }
    print(f"this is the method -> {request_data['method']}")
    print(f"this is the headers -> {request_data['headers']}")
    print(f"this is the data -> {request_data['data']}")
    print(f"this is the url -> {request_data['url']}")
    print("")

    # Pass the event to the reverse proxy and get the response
    proxy_response = proxy.run(request_data, page_title=None, text_replaces=None)
    return proxy_response

    
    # Flask will use the response data returned from the proxy
    #return jsonify(json.loads(proxy_response['body'])), proxy_response['statusCode']


if __name__ == '__main__':
    print('checkpoint 1 - dependencies handled')
    app.run(port=5001)
