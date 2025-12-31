import json
import logging
import requests
from typing import Optional, Dict, Any
from reverse_proxy.validate import is_valid_url
from reverse_proxy.config.logging import pipeline_logger


def prepare_request_body(data: Any, headers: Optional[Dict]) -> Any:
    """Prepare request based on content type"""
    if data is None:    
        return None
    
    content_type = headers.get("Content-Type", "") if headers else ""

    if isinstance(data, dict) and "application/json" in content_type:
        return json.dumps(data)

    return data 


def execute_request(method: str, url: str, params=None, data=None, headers=None) -> requests.Response:
    """Execute HTTP request to target server"""
    if not is_valid_url(url): 
        raise ValueError(f"Invalid URL: {url}")

    prepared_data = prepare_request_body(data, headers)

    pipeline_logger.info(f"Executing: {method.upper()} {url}")

    try: 
        response = requests.request(
            method=method.upper(), 
            url=url,
            params=params,
            data=prepared_data, 
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response

    except requests.exceptions.RequestException as e: 
        pipeline_logger.error(f"Request failed: {e}")
        raise


def parse_response(response: requests.Response) -> Dict: 
    """Parse HTTP response into structured dict"""
    content_type = response.headers.get("Content-Type", "")

    result = {
        "status_code": response.status_code, 
        "headers": dict(response.headers), 
        "content_type": content_type, 
        "text": response.text,
        "json": None, 
        "content": None
    }

    if "application/json" in content_type:
        try: 
            result["json"] = response.json()
            result["content"] = result["json"]
            pipeline_logger.info("Parsed JSON response")
        except json.JSONDecodeError:
            result["content"] = response.text
            pipeline_logger.warning("Failed to parse JSON, using text")

    
    elif "text" in content_type or "html" in content_type: 
        result["content"] = response.text
        pipeline_logger.info("Parsed text/HTML response")


    else: 
        result["content"] = response.text
    
    return result