from typing import List, Dict

from ...input import ParamType
from ...config import ConfigBase

class ParamAnalyzerConfig(ConfigBase):
    """Param analyzer moudle configuration.
    
    Attributes:
        providers (list[str]) - names of param value providers to use.
        ignore_params (dict[param_type,list[str]]) - blacklist of params to exclude from analysis (grouped by param_type)
    """
    
    providers: List[str]
    ignore_params: Dict[ParamType, List[str]]
    
    @staticmethod
    def default() -> 'ParamAnalyzerConfig':
        return ParamAnalyzerConfig(providers=[], ignore_params={})
    
    