from pydantic import BaseModel
from typing import Optional, Dict

from ...param_usage import ParamUsageInfo

from .output_info import OutputInfo

class ScanReport(BaseModel):
    """Scan report.
    
    Attributes:
        output_info (OutputInfo) - captured project output information
        coverage_id (str) - captured coverage id
        param_usages (dict[str,ParamUsageInfo]) - captured param usage information
    """
    
    output_info: Optional[OutputInfo] = None
    coverage_id: Optional[str] = None
    param_usages: Optional[Dict[str, ParamUsageInfo]] = None
    
