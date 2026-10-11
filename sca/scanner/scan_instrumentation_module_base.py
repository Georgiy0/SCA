from abc import abstractmethod
from typing import List

from ..core import ModuleBase
from ..input import InputInfo

from .entity import OutputInfo
from .entity.scan_report import ScanReport
from .entity import InstrumentationCapability, Stand
from .sender_base import SenderBase

class ScanInstrumentationModuleBase(ModuleBase):
    """Declares API for scan instrumentation modules.
    """
    
    @property
    @abstractmethod
    def Name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def Capabilities(self) -> List[InstrumentationCapability]:
        pass

    @abstractmethod
    def pre_send_action(self, input_id: str, input: InputInfo, sender: SenderBase, stand: Stand) -> None:
        pass

    @abstractmethod
    def post_send_action(self, input_id: str, input: InputInfo, output: OutputInfo, sender: SenderBase, stand: Stand) -> None:
        pass
    
    @abstractmethod
    def populate_scan_report(self, input_id: str, input: InputInfo, output: OutputInfo, report: ScanReport, sender: SenderBase, stand: Stand) -> None:
        pass
    
    