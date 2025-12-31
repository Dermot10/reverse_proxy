
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from typing import Dict, Optional, Any, Callable
from reverse_proxy.config.logging import pipeline_logger

def update_html_title(html: str, new_title: str) -> str:
    """update HTML page title"""
    soup = BeautifulSoup(html, "html_parser")
    if soup.title:
        soup.title.string = new_title
        pipeline_logger.info(f"Updated title: {new_title}")
    return str(soup)

def replace_text(text: str, replacements: Dict[str, str]) -> str: 
    """Replace text based on replacement dict"""
    result = text 
    for old, new in replacements.items(): 
        result = result.replace(old, new)
        pipeline_logger.info(f"Replaced: '{old}' -> '{new}'")
    return result 

def transform_response(response: Dict, page_title: Optional[str] = None, text_replaces: Optional[Dict] = None) -> Dict: 
    """Transform response content (HTML manipulation, text replacememt)"""
    content_type = response.get("content_type", "")

    if "text" not in content_type and "html" not in content_type: 
        pipeline_logger.warning(f"Cannot transform: {content_type}")
        return response
    
    text = response.get("text", "")
    if not text: 
        return response
    
    try:
        if page_title: 
            text = update_html_title(text, page_title)
        
        if text_replaces and isinstance(text_replaces, dict): 
            text = replace_text(text, text_replaces)

        response["text"] = text
        response["content"] = text

        return response

    except Exception as e: 
        pipeline_logger.error(f"Transformation failed: {e}")
        return response