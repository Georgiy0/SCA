from enum import Enum

class ParamType(str, Enum):  
    # internal
    CREDS = "creds"
    
    # TCP
    SOCKET_ADDR = "socket_addr",
    SOCKET_PORT = "socket_port",
    
    # HTTP
    METHOD = "method"
    URI = "uri"
    QUERY = "query"
    QUERY_STRING = "query_string" # the whole query string
    FORM = "form"
    FORM_FILE = "form_file"
    HEADER = "header"
    COOKIE = "cookie"
    
    # HTTP AUTH
    AUTH_DIGEST = "auth_digest"
    HTTP_AUTH_USER = "http_auth_user"
    HTTP_AUTH_PASSWORD = "http_auth_password"
    
    # PHP SPECIFIC
    PATH_INFO = "php_path_info" # e.g. /some/file.php/PATH/INFO
    
    

    