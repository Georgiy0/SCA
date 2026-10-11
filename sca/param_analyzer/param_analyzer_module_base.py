from abc import abstractmethod

from ..core import ModuleBase

from .param_analyzer_observer_base import ParamAnalyzerObserverBase

class ParamAnalyzerModuleBase(ModuleBase):
    """Declares API for param analysis module.
    """
    
    @abstractmethod
    def analyze(self, observer: ParamAnalyzerObserverBase | None) -> int:
        pass
    