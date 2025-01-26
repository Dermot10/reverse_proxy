from urllib.parse import urljoin

from .processes.Request_Receive import RequestReceive
from .processes.Request_Execute import RequestExecute
from .processes.Response_Transform import ResponseTransform


class ReverseProxyRequestResponse:

    def __init__(self):
        """Inject Dependencies into class constructor for the process classes decoupling workflows"""
        self.request_receive = RequestReceive(self)
        self.request_execute = RequestExecute()
        self.response_transform = ResponseTransform(self)

    def run__via__target_site__path(self, method, target_site, path, params=None, data=None, headers=None):

        url = urljoin(target_site, path)
        self.request_execute.setup(
            method=method, url=url, params=params, data=data, headers=headers)
        self.request_execute.run()
        return self.request_execute.response()
