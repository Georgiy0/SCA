from abc import abstractmethod
from typing import List, Dict

from ..core import ModuleBase
from ..input import InputParam, ParamType

from .entity import ParamUsages, TraceFrame

class ParamUsagesModuleBase(ModuleBase):
    """Declares API for param usages module.
    """
    
    @abstractmethod
    def add_param_usage(self, input_id: str, param: InputParam, trace: List[TraceFrame]) -> bool:
        pass
    
    @abstractmethod
    def get_param_usages(self) -> ParamUsages:
        pass
    
    @abstractmethod
    def get_ignore_param_trace_frames(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_dropped_param_trace_frames(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_param_usage_traces_dot_graph(self) -> str:
        pass
    
    @abstractmethod
    def get_param_getter_wrapper_candidates(self) -> Dict[str, List[ParamType]]:
        pass
    
    @abstractmethod
    def add_param_usages_to_notes(self) -> int:
        pass