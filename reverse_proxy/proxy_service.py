import logging
from typing import Callable, Dict, Optional
from reverse_proxy.config.consts import ROUTE_CONFIG
from reverse_proxy.validate import validate_event
from reverse_proxy.router import route_to_target
from reverse_proxy.execution import execute_request, parse_response
from reverse_proxy.transformation import transform_response

logging.basicConfig(level=logging.INFO)
pipeline_logger = logging.getLogger(__name__)



# proxy service takes place here, 
# pipeline process, agnostic to any handlers, process only, pure funcs called.

def proxy_request(event: Dict, transform_options: Optional[Dict] = None, route_config: Dict = ROUTE_CONFIG) -> Dict: 
    """Main proxy function - coordinated the request pipeline
    
    Pipeline: validate -> route -> execute -> parse -> transform (Optional)

    Args: 
        events: Request event with method, path, params, data, headers
        transform_options: Optional dict with page_title and/or text_replaces
        route_config: Path-to-URL mapping

    Returns:
        Response dict with status_code, headers, content, etc.     
    """

    try: 
        validated = validate_event(event)

        target_url = route_to_target(validated["path"], route_config)

        raw_response = execute_request(
            method=validated["method"], 
            url=target_url, 
            params=validated.get("params"),
            data=validated.get("data"), 
            headers=validated.get("headers")
        )

        response = parse_response(raw_response)

        if transform_options: 
            response = transform_response(
                response, 
                page_title=transform_options.get("page_title"), 
                text_replaces=transform_options.get("text_replaces")
            )
        
        pipeline_logger.info(f"Successfully proxied to {target_url}")

        return response 

    except Exception as e: 
        pipeline_logger.error(f"Proxy error: {e}", exc_info=True)
        raise

        