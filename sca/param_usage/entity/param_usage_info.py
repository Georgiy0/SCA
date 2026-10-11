from pydantic import BaseModel
from typing import List
import hashlib
import json

from ...input import InputParam

from .trace_frame import TraceFrame, trace_frame_adapter

class ParamUsageInfo(BaseModel):
    """Param usage information.
    
    Attributes:
        analyzed (bool) - wheather param usage was analyzed. TODO: move to param analysis module's cache
        param (InputParam) - param that was used by the project
        trace (list[TraceFrame]) - stack trace to param usage location in project codebase
    """
    
    analyzed: bool
    param: InputParam
    trace: List[TraceFrame]
    
    def get_hash(self) -> str:
        hash_data = {
            "param_name": self.param.name,
            "param_type": self.param.param_type,
            "trace": trace_frame_adapter.dump_python(self.trace)
        }
        json_str = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    