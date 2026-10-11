from abc import ABC, abstractmethod
from pydantic import BaseModel

from ..input import InputParam, InputInfo

class ParamAnalyzerStatus(BaseModel):
    """Param analysis status to report via observer interface.
    """
    
    current_param: InputParam
    current_input: InputInfo
    unique_params_total: int
    unique_params_cnt: int
    new_candidates: int
    new_candidates_tested: int
    new_cnt: int


class ParamAnalyzerObserverBase(ABC):
    """Declares observer interface for UI components.
    """
    
    @abstractmethod
    def update_status(self, status: ParamAnalyzerStatus) -> None:
        pass
    
    @abstractmethod
    def update_frequence(self) -> int:
        pass
    
    