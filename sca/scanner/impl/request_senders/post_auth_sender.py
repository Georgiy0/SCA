from ..requests_sender_base import HttpRequestsSender

from .post_auth_sender_config import PostAuthSenderConfig

class PostAuthRequestsSender(HttpRequestsSender):
    """Implement HTTP request sender with POST request based authentication with cookie session storage.
    """
    
    cSenderName = "postauthcookie"

    def __init__(self):
        super().__init__()
        self.__config: PostAuthSenderConfig = None
        self.__authenticated_once = False

    @property
    def Name(self) -> str:
        return PostAuthRequestsSender.cSenderName

    def init_sender(self, config_module, logging_module):
        self.__config = config_module.get_config_or_default(PostAuthSenderConfig, PostAuthSenderConfig.default())
        self.__logger = logging_module

    def init_session(self, stand, session, creds):
        params = self.__config.post_data
        for key in params:
            params[key] = params[key]\
                            .replace(self.__config.username_placeholder, creds.username)\
                            .replace(self.__config.password_placeholder, creds.password)
        self.__logger.log_trace(f"sending auth request via {self.__class__.Name}")
        self.__logger.log_trace(f"AUTH URL: {self.__config.auth_uri}")
        self.__logger.log_trace(f"AUTH DATA: {params}")
        r = session.post(f"{stand.base_uri}{self.__config.auth_uri}", data=params, verify=False, allow_redirects=False)
        if r.status_code != self.__config.auth_valid_status:
            self.__logger.log_error(f"invalid auth status code {r.status_code}. exptected {self.__config.auth_valid_status}")
            return False
        if r.status_code in [301, 302, 303] and ("Location" not in r.headers or r.headers["Location"] != self.__config.auth_valid_redirect):
            self.__logger.log_error(f"invalid auth redirecation location '{r.headers['Location']}'. expected '{self.__config.auth_valid_redirect}'")
            return False
        self.__authenticated_once = True
        return self.check_session(session)

    def check_session(self, session):
        if not self.__authenticated_once:
            return False
        cookies_dict = session.cookies.get_dict()
        for cookie_name in self.__config.session_cookies:
            if cookie_name not in cookies_dict:
                self.__logger.log_error(f"missing session cookie '{cookie_name}' after login request")
                return False
        return True
    
