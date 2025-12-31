from typing import Dict
from urllib.parse import urlparse
from reverse_proxy.config.consts import VALID_METHODS
from reverse_proxy.config.logging import pipeline_logger

def validate_event(event: Dict) -> Dict: 
    """Validate incoming event structure and content"""

    if not isinstance(event, dict): 
        raise ValueError("Event must be of type dict")
    
    required_fields = ["method", "path"]
    for field in required_fields: 
        if field not in required_fields:
            raise ValueError(f"Missing required field: {field}")

    method = event["method"].upper()
    if method not in VALID_METHODS: 
        raise ValueError(f"Invalid HTTP method: {method}")
    
    if "headers" in event and not isinstance(event["headers"], dict):
        raise ValueError("Headers must be a dictionary")

    pipeline_logger.info(f"Validated: {method} {event['path']}")
    return event


def is_valid_url(url: str) -> bool: 
    """Check if URL is probably formatted"""
    result = urlparse(url)
    return result.scheme in ["http", "https"] and bool(result.netloc)