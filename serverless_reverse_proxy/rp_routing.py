import json
import logging
import requests
from severless_reverse_proxy.proxy_interface import ReverseProxyInterface


class ReverseProxy(ReverseProxyInterface):
    """Extends Reverse Proxy interface, routing logic for incoming events"""

    def __init__(self):
        super().__init__()
        self.route_config = {
            "/google": "https://www.google.com",
            "/hollandandbarrett": "https://www.hollandandbarrett.com/",
            "/youtube": "https://www.youtube.com"
        }

    def select_target_endpoint(self, path):
        """Match the request path to a configured endpoint"""
        if path in self.route_config:
            logging.info(f"Matched path {path} to target endpoint: {self.route_config[path]}")
            return self.route_config[path]
        else:
            logging.error(f"Invalid path {path}. Available paths: {', '.join(self.route_config.keys())}")
            return None

    def validate_event(self, event):
        """Validate incoming event to ensure it has the required fields"""
        required_fields = ['httpMethod', 'path']
        for field in required_fields:
            if field not in event:
                raise ValueError(f"Missing required field: {field}")
        logging.info(f"Validated event with method {event['httpMethod']} and path {event['path']}")

    def extract_request_data(self, event):
        """Extracts HTTP method, URL, request body, and headers from the event, then forwards the request"""
        try:
            # Step 1: Validate the event input
            self.validate_event(event)

            # Step 2: Extract HTTP method and path
            http_method = event['httpMethod']
            path = event['path']

            # Step 3: Map the path to the corresponding target endpoint
            target_url = self.select_target_endpoint(path)
            if not target_url:
                return self.generate_error_response(404, 'Invalid path')

            # Step 4: Prepare request data
            request_body = event.get('body', None)
            request_headers = event.get('headers', {})

            # Log the outgoing request details
            logging.info(f"Forwarding {http_method} request to {target_url} with body: {request_body}")

            # Step 5: Forward the request to the target URL
            response = requests.request(http_method, target_url, data=request_body, headers=request_headers)

            # Step 6: Prepare and return the response
            return self.generate_success_response(response)

        except Exception as e:
            logging.error(f"Error during request handling: {str(e)}", exc_info=True)
            return self.generate_error_response(500, str(e))

    def generate_success_response(self, response):
        """Generate a successful response for API Gateway"""
        return {
            'statusCode': response.status_code,
            'headers': {
                'Content-Type': response.headers.get('Content-Type', 'application/json')
            },
            'body': response.text
        }

    def generate_error_response(self, status_code, message):
        """Generate an error response for API Gateway"""
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': message})
        }


# Example usage for testing
if __name__ == '__main__':
    proxy = ReverseProxy()

    # Example event data simulating API Gateway request
    event = {
        'httpMethod': 'GET',
        'path': '/google',
        'body': None,
        'headers': {'Accept': 'application/json'}
    }

    # Simulate invoking the reverse proxy
    response = proxy.extract_request_data(event)
    print(response)