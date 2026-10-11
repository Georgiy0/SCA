from abc import abstractmethod
from typing import List

from ..core import ModuleBase

from ..input import InputInfo

from ..param_usage import ParamUsageInfo

class ParamValueProviderModuleBase(ModuleBase):
    """Declares param value mutator interface for param analyzis module
    """
    
    @property
    @abstractmethod
    def Name(self) -> str:
        pass
    
    @abstractmethod
    def get_input_candidates(self, input: InputInfo, param_usage_info: ParamUsageInfo) -> List[InputInfo]:
        pass
    
    