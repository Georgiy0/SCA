from abc import abstractmethod
from typing import List

from ..core import ModuleBase
from ..input import InputInfo

from .entity import ScanReport
from .entity import InstrumentationCapability

class ScannerModuleBase(ModuleBase):
    """Declares API for scanner module.
    """
    
    @abstractmethod
    def scan(self, input: InputInfo) -> None:
        pass
    
    @abstractmethod
    def peek_scan(self, input: InputInfo, allowed_capabilities: List[InstrumentationCapability] = None) -> ScanReport:
        pass

    @abstractmethod
    def replay(self, input: InputInfo) -> None:
        pass
    
    