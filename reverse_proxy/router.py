from typing import Dict

from reverse_proxy.config.consts import ROUTE_CONFIG
from reverse_proxy.config.logging import pipeline_logger

def route_to_target(path:str, route_config: Dict = ROUTE_CONFIG) -> str: 
    """Map request path to target URL"""
    if path not in route_config: 
        available = ", ".join(route_config.keys())
        raise ValueError(f"Unknown path: {path}, Available: {available}")

    target_url = route_config[path]
    pipeline_logger.info(f"Routed: {path} -> {target_url}")
    return target_url