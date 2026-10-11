from pydantic import BaseModel
from typing import Optional

from .param_type import ParamType

class InputParam(BaseModel):
    """Represents an abstract input parameter.
    
    Attributes:
        param_type - parameter type (semantics). E.g. HTTP URI, HTTP query paramter
        name - parameter name. E.g. query paramter name
        value - paramter value
        
    Note:
        name may be empty for prameter types that do not provide unique param identifiers.
        E.g. HTTP METHOD param will define only value (the name will be empty).
    """
    
    param_type: ParamType
    name: str
    value: Optional[str] = None

