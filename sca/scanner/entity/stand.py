from pydantic import BaseModel
from typing import List

from ...core import ScaError

from .credentials_set import CredentialsSet

class Stand(BaseModel):
    """Describes remote web application information for scanning.
    
    Attributes:
        base_uri (str) - web application root URI
        domain (str) - web application domain
        creds (list[CredentialSet]) - list of credentials for configured web application
    """
    
    base_uri: str
    domain: str
    creds: List[CredentialsSet] = []

    def get_creds(self, name: str) -> CredentialsSet | None:
        creds = [c for c in self.creds if c.name == name]
        if len(creds) == 0:
            return None
        elif len(creds) > 1:
            raise ScaError(f"More than one credential set with name '{name}'")
        else:
            return creds[0]
        
