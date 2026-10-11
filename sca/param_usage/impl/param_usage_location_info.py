from pydantic import BaseModel
from typing import List, Dict

from ..entity import ParamUsageInfo

class ParamUsageLocationInfo(BaseModel):
    """Represents a node in param usage stack trace graph that is used to find wrapper function for param getters.
    
    Attributes:
        location (str) - lcoation in project codebase (stack frame locaotin - file:line)
        trace_depth (int) - strack frame depth
        usages (list[ParamUsageInfo]) - list of params that are used through this stack frame location
        children (dict[str,ParamUsageLocationInfo]) - links to children nodes (child location -> child node)
    """
    
    location: str
    trace_depth: int
    usages: List[ParamUsageInfo]
    children: Dict[str, "ParamUsageLocationInfo"]
    
    