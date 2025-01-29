import json
import sys
import os
import logging
import requests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from serverless_reverse_proxy.proxy_interface import ReverseProxyInterface
from serverless_reverse_proxy.processes.Response_Transform import ResponseTransform


# take input from flask server and passes off to this class
# 
# validate request receieve
# request execute 
# response transform  



class LocalReverseProxy(ReverseProxyInterface):
    """Concrete Reverse Proxy, routing logic for incoming events"""

    def __init__(self):
        super().__init__()
        self.route_config = {
            "/google": "https://www.google.com",
            "/hollandandbarrett": "https://www.hollandandbarrett.com/",
            "/youtube": "https://www.youtube.com",
            "/jsonplaceholder": "https://jsonplaceholder.typicode.com/posts"
        }
        
    def select_target_endpoint(self, path) -> str:
        """Match the request path to a configured endpoint"""
        if path in self.route_config:
            logging.info(f"Matched path {path} to target endpoint: {self.route_config[path]}")
            return self.route_config[path]
        else:
            logging.error(f"Invalid path {path}. Available paths: {', '.join(self.route_config.keys())}")
            return None

    def stringify_event_body(self, event) -> str: 
        """Stringify the event body for the request if type dict, in place transformation"""
        headers = event.get('headers', {})
        if 'Content-Type' in headers and headers['Content-Type'] == 'application/json': 
            if isinstance(event.get('data'), dict):
                event['data'] = json.dumps(event['data'])
            elif isinstance(event.get('data'), str):
                # If the data is already a string, don't do anything.
                pass

    def validate_request_event(self, event) -> bool: 
        """"""
        is_valid = self.reverse_proxy.request_receive.validate(event)
        print(f'Event validation result: {is_valid}')

    def process_request_event(self, event):
        """"""
        processed_event = self.reverse_proxy.request_receive.run(event)
        print(f'Event processed, returned payload result: {processed_event}')

    def process_request_execution(self, event):
        """Utilise set up function for request http validation and execution"""
        path = self.select_target_endpoint(event['url'])
        try: 
            self.stringify_event_body(event) # for a uniform request body 

            self.reverse_proxy.request_execute.setup(
                method=event['method'], 
                url=path, 
                params=event.get("params"),
                data=event.get("data"),
                headers=event.get('headers')
            )


            print(event.get('headers'))
            request_kwargs=self.reverse_proxy.request_execute.run()
            print(request_kwargs.raw_response)
            response = self.reverse_proxy.request_execute.response()
            print('\ncheckpoint 3 \n')
            return response
        except Exception as e: 
            return {'error': str(e)}


    def process_response_transformation(self, event, page_title=None, text_replaces=None):
        """Transform the HTTP response using ResponseTransform"""

        response = self.process_request_execution(event)
        if page_title or text_replaces: 
            text_response = self.reverse_proxy.response_transform.execute_transformation_request(response)
            updated_response = self.reverse_proxy.response_transform.text(text_response, page_title, text_replaces)
            return updated_response
        else: 
            logging.warning("Transformation failed; returning original response.")
            return response

      


    def run(self, event, page_title=None, text_replaces=None):
        """Main entry point for the reverse proxy"""

        # Apply response transformation if applicable
        if page_title is not None and text_replaces is not None:
            transformed_response = self.process_response_transformation(
                event=event,
                page_title=page_title,
                text_replaces=text_replaces
            )
            return transformed_response
        else: 
            response = self.process_request_execution(event)
            return response
        

# Example usage for testing
if __name__ == '__main__':
    proxy = LocalReverseProxy()

    #Example event data simulating API Gateway request, 
    #Serverresponse model - accept text/html
    event = {
        'method': 'GET',
        'url': '/google',
        'data': None,
        'headers': {'Content-Type': 'application/json'}
    }

    # Post application/json but body is text/html
    event_2 = {
        'method': 'POST',
        'url': '/jsonplaceholder',
        'body': '{"userId": 1, "title": "foo", "body": "bar"}',
        'headers': {'Content-Type': 'application/json'}
    }

    # Post application/json and body is json 
    event_3 = {
        "method": "POST",
        "url": "/jsonplaceholder",
        "params": {"userId": 1},
        "data": {"title": "foo", "body": "bar", "userId": 1},
        "headers": {'Content-Type': 'application/json'}
    }

    # GET text/html and the response is transformed
    # Bs4 Requires specific html/text elements to exist
    event_transformed = {
        'method': 'GET',
        'url': '/google',  # Matches the route_config in the proxy
        'headers': {'Content-Type': 'text/html'},
        'page_title': 'My Custom Page Title',  # New page title to be set
        'text_replaces': {
            'Google': 'MyCustomSearchEngine',  # Replace "Google" with this
        }   
    }

    # response = proxy.run(event_3)
    response = proxy.run(event_transformed,
                    page_title=event_transformed.get("page_title"),
                    text_replaces=event_transformed.get("text_replaces")
                    )
    print(response)
    
    