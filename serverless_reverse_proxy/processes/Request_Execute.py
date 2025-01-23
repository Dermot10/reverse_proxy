import requests
from urllib.parse import urlparse


class RequestExecute:

    def __init__(self):
        self.method = None
        self.url = None
        self.params = None
        self.data = None
        self.headers = None
        self.raw_response = None

    def is_valid_url(self, url):
        """Validate URL format."""
        result = urlparse(url)
        return all([result.scheme, result.netloc])

    def is_valid_method(self, method):
        """Validate HTTP method."""
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        return method.upper() in valid_methods

    def is_valid_headers(self, headers):
        """Validate headers as a dictionary with non-empty string keys and values."""
        if not isinstance(headers, dict):
            return False
        for key, value in headers.items():
            if not isinstance(key, str) or not isinstance(value, str):
                return False
        return True

    def setup(self, method, url, params=None, data=None, headers=None):
        """Set up execution of request, deconstructing and validating incoming request"""
        # Validate HTTP method
        if not self.is_valid_method(method):
            raise ValueError(f"Invalid HTTP method: {method}")

        # Validate URL
        if not self.is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")

        # Validate headers (if provided)
        if headers and not self.is_valid_headers(headers):
            raise ValueError("Headers must be a dictionary with non-empty string keys and values.")

        self.method = method
        self.url = url
        self.params = params
        self.data = data  # todo: add validation to check if it is valid post data (according to provided headers)
        self.headers = headers
        return self

    def run(self):
        """Executes HTTP request to destination, adds response to instance and returns"""
        kwargs = dict(method=self.method,
                      url=self.url,
                      params=self.params,
                      data=self.data,
                      headers=self.headers)
        self.raw_response = requests.request(**kwargs)  # send request with incoming parameters and return response
        return self

    def response(self):
        """Extracts response metadata to be sent back to client"""
        if self.raw_response is None:
            return {}

        status_code = self.raw_response.status_code
        headers = dict(self.raw_response.headers)
        content_type = headers.get('Content-Type')
        text = ''
        json = None
        content = None
        if content_type and content_type.startswith('application/json'):
            text = self.raw_response.text
            json = self.raw_response.json()
        else:
            text = self.raw_response.text

        return dict(content_type=content_type,
                    status_code=status_code,
                    content=content,
                    json=json,
                    text=text,
                    headers=headers)
