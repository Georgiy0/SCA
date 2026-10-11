from abc import abstractmethod
from typing import Dict
import requests

from ...input import ParamType, InputInfo
from ...core import ScaError

from ..entity import CredentialsSet, Stand
from ..entity import OutputInfo, OutputElem, OutputElemType
from ..sender_base import SenderBase

class HttpRequestsSender(SenderBase):
    """Implements base for HTTP input senders via requests library.
    """
    
    cPreAuthCredsName = "preauth"

    def __init__(self):
        super().__init__()
        self.__sessions: Dict[str, Dict[str, requests.Session]] = {}

    def get_session(self, stand: Stand, creds_name: str) -> requests.Session:
        if stand.base_uri not in self.__sessions:
            self.__sessions[stand.base_uri] = {}
        creds = stand.get_creds(creds_name)
        if creds is None and creds_name != HttpRequestsSender.cPreAuthCredsName:
            raise ScaError(f"No credential set '{creds_name}' for stand '{stand.base_uri}'")
        if creds_name not in self.__sessions[stand.base_uri]:
            self.__sessions[stand.base_uri][creds_name] = requests.Session()
        return self.__sessions[stand.base_uri][creds_name]

    def __make_request(self, stand: Stand, input: InputInfo) -> requests.Request:
        method = input.get_param_of_type(ParamType.METHOD)
        uri = input.get_param_of_type(ParamType.URI)
        query_params = input.get_params_of_type(ParamType.QUERY)
        cookies_raw = input.get_params_of_type(ParamType.COOKIE)
        req_cookies = requests.cookies.RequestsCookieJar()

        for name, value in cookies_raw.items():
            req_cookies.set(name, value, domain=stand.domain, path="/")

        headers_raw = input.get_params_of_type(ParamType.HEADER)
        headers = {}
        for header_name, header_value in headers_raw.items():
            headers[header_name] = header_value

        request = requests.Request(
            method=method,
            url=f"{stand.base_uri}{uri}",
            params=query_params,
            cookies=req_cookies,
            headers=headers
        )
        if method != "POST":
            request.method = "POST" # TODO: mb it's better to create explicit input with POST somewhere else instead?
            request.data = input.get_params_of_type(ParamType.FORM)
        return request
    
    @abstractmethod
    def init_session(self, stand: Stand, session: requests.Session, creds: CredentialsSet) -> bool:
        pass

    @abstractmethod
    def check_session(self, session: requests.Session) -> bool:
        pass

    def send_input(self, stand, input):
        creds_name = input.get_param_of_type_or_default(ParamType.CREDS)
        if creds_name is None:
            creds_name = HttpRequestsSender.cPreAuthCredsName

        current_req = self.__make_request(stand, input)
        current_session = self.get_session(stand, creds_name)
        if creds_name != HttpRequestsSender.cPreAuthCredsName:
            creds = stand.get_creds(creds_name)
            if not self.check_session(current_session) and not self.init_session(stand, current_session, creds):
                raise ScaError(f"failed to initialize session with scanner {self}")
        prepared_request = current_session.prepare_request(current_req)

        resp = current_session.send(prepared_request, verify=False, allow_redirects=False, timeout=90) # TODO: from config
        
        output = OutputInfo(elements=[])
        output.elements.append(OutputElem(elem_type=OutputElemType.STATUS, name="", value=str(resp.status_code)))
        for h, v in resp.headers.items():
            output.elements.append(OutputElem(elem_type=OutputElemType.HEADER, name=h, value=v))
        return output
    
    def send_raw(self, stand, input):
        current_req = self.__make_request(stand, input)
        with requests.Session() as session:
            resp = session.send(current_req.prepare(), verify=False, allow_redirects=False, timeout=90) # TODO: from config
        return (resp.status_code, resp.content)
        
