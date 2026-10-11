from typing import Dict, List, Optional

from ....config import ConfigBase

class PostAuthSenderConfig(ConfigBase):
    """PostAuthSencder configuration.
    
    Attributes:
        auth_uri (str) - URI to authentication handler
        auth_valid_status (int) - HTTP status for valid authentication completion
        auth_valid_redirect (str | None) - valid Location (redirection) string (if valid status is redirection based (301, 302, 303))
        post_data (dict[str,str]) - template of post data for auth request (should use placeholders for username and password values)
        username_palceholder (str) - placeholder for username vlaue
        password_placeholder (str) - placeholder for password vlaue
        session_cookies (list[str]) - names of session cookies
    """
    
    auth_uri: str
    auth_valid_status: int
    auth_valid_redirect: Optional[str] | None = None
    post_data: Dict[str,str]
    username_placeholder: str
    password_placeholder: str
    session_cookies: List[str]

    @staticmethod
    def default() -> 'PostAuthSenderConfig':
        return PostAuthSenderConfig(auth_uri='/auth/uri', auth_valid_status=302,\
                              auth_valid_redirect='index.php',\
                              post_data={
                                    "username": "UNAME",
                                    "password": "UPWD",
                                    "submit": "login"
                              },\
                              username_placeholder="UNAME",\
                              password_placeholder="UPWD",\
                              session_cookies=["PHPSESSID"])

