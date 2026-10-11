from pydantic import BaseModel
from typing import Dict

from .param_usage_info import ParamUsageInfo

class ParamUsages(BaseModel):
    """All param usages.
    
    Attributes:
        param_usages (dict[str,dict[str,ParamUsageInfo]]) - input_id -> param_usage_hash -> param usage info
    """
    
    param_usages: Dict[str, Dict[str, ParamUsageInfo]]
    
    