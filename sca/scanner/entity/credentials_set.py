from pydantic import BaseModel

class CredentialsSet(BaseModel):
    """Credentials for authentication.
    
    Attribute:
        name (str) - credential set identifier
        username (str), password (str) - credentials
    """
    
    name: str
    username: str
    password: str

    