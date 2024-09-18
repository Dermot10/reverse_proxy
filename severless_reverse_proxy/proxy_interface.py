from .rp_request_response import ReverseProxyRequestResponse


class ReverseProxyInterface:
    """Main interface for Reverse Proxy, instantiates individual processes"""

    def __init__(self):
        # self.target_site = target_site
        self.reverse_proxy = ReverseProxyRequestResponse()
