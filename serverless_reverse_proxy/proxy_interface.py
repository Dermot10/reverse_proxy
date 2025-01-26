from .rp_request_response import ReverseProxyRequestResponse
from abc import ABC


class ReverseProxyInterface:
    """Main interface for Reverse Proxy, instantiates individual processes"""
    """ # Abstract class, will enforce specific methods"""

    def __init__(self):
        # self.target_site = target_site
        self.reverse_proxy = ReverseProxyRequestResponse()
