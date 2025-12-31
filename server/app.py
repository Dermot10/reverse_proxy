import os
import sys
import json
from flask import Flask, jsonify, request, Response
from reverse_proxy.config.logging import adapter_logger
from reverse_proxy.config.consts import ROUTE_CONFIG
from reverse_proxy.proxy_service import proxy_request


# Go server equivalent used for local development. 
app = Flask(__name__) 




@app.route('/proxy', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def handle_proxy():
    """
    Flask route to handle proxying requests
    
    Expects JSON body with:
    {
        "path": "/google",
        "params": {"key": "value"},  # optional
        "data": {"body": "data"},     # optional
        "transform_options": {        # optional
            "page_title": "New Title",
            "text_replaces": {"old": "new"}
        }
    }
    """
    try: 
        payload = request.get_json(force=True, silent=True) or {}

        # Dummy event to test reverse proxy
        event = {
            "method": request.method,
            "path": payload.get("path"),
            "params": payload.get("params"),
            "data": payload.get("data"),
            "headers": payload.get("headers", {"content-Type": "application/json"})
        }


        transformation_options = payload.get("transformation_options")

        adapter_logger.info(f"Flask received: {request.method} {event['path']}")
        
        response = proxy_request(event, transformation_options)

        return jsonify({
            "status": "success", 
            "status_code": response["status_code"],
            "content_type": response["content_type"], 
            "content": response["content"], 
            "headers": response["headers"]
        }), response["status_code"]

    except ValueError as e: 
        adapter_logger.error(f"Validation error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

    except Exception as e:
        adapter_logger.error(f"Proxy error: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500 



@app.route("/proxy/<path:target_path>", methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def handle_proxy_with_path(target_path): 
    """
    Alternative route using URL path for target selection

    Headers are currently skipped for response chunking purposes

    Example: GET /proxy/google?key=value
    """

    try: 
        # Get headers but filter out Flask/client-specific ones
        headers = dict(request.headers)
        
        # Remove headers that shouldn't be forwarded
        headers_to_skip = [
            'Host',
            'Content-Length',
            'Connection',
            'Accept-Encoding',
            'Transfer-Encoding'
        ]
        
        for header in headers_to_skip:
            headers.pop(header, None)

        event = {
            "method": request.method,
            "path": "/" + target_path,
            "params": dict(request.args), 
            "data": request.get_json(silent=True), 
            "headers": dict(request.headers)
        }

        transform_options = None
        if request.args.get("page_title") or request.args.get("text_replace"): 
            transform_options = {
                "page_title": request.args.get("page_title"), 
                "text_replace": json.loads(request.args.get("text_replace", "{}"))
            }

        adapter_logger.info(f"Flask received: {request.method} / {target_path}")

        response = proxy_request(event, transform_options)

        content = response['content']
        
        if isinstance(content, (dict, list)):
            content = json.dumps(content)
            content_type = 'application/json'
        elif content is None:
            content = ''
            content_type = response['content_type']
        else:
            content_type = response['content_type']
        
        # Content in bytes  d
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        # Create response with explicit content length
        flask_response = Response(
            content,
            status=response['status_code']
        )
        flask_response.headers['Content-Type'] = content_type
        flask_response.headers['Content-Length'] = len(content)
        
        return flask_response


    except ValueError as e: 
        adapter_logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    
    except Exception as e: 
        adapter_logger.error(f"Proxy error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500 

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "reverse-proxy", 
        "routes": list(ROUTE_CONFIG.keys())
        }), 200 


@app.route("/routes", methods=["GET"])
def list_routes(): 
    """List available proxy routes"""
    return jsonify({
        "available_routes": ROUTE_CONFIG
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    adapter_logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500



if __name__ == '__main__':
    adapter_logger.info("Starting Flask Reverse Proxy Server...")
    adapter_logger.info(f"Available routes: {list(ROUTE_CONFIG.keys())}")
    
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=5001,
        debug=True
    )