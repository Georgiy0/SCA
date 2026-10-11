from typing import List

from ...config import ConfigBase

class ParamUsagesConfig(ConfigBase):
    """Param analyzer moudle configuration.
    
    Attributes:
        param_trace_ignore_frame (list[str]) - trace locations to ignore when evaluating unique param usages (i.e. wrapper trace frames)
        param_trace_drop (list[str]) - trace location to ignore param completly
    """
    
    param_trace_ignore_frame: List[str]
    param_trace_drop: List[str]
    
    @staticmethod
    def default() -> 'ParamUsagesConfig':
        return ParamUsagesConfig(param_trace_ignore_frame=["file:line"], param_trace_drop=["file:line"])
    
    