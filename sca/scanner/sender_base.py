from abc import ABC, abstractmethod
from typing import Tuple

from ..input import InputInfo
from ..config import ConfigModuleBase
from ..logging import LoggingModuleBase

from .entity import OutputInfo, Stand

class SenderBase(ABC):
    """Declares API for input senders.
    """
    
    @property
    @abstractmethod
    def Name(self) -> str:
        pass

    @abstractmethod
    def init_sender(self, config_module: ConfigModuleBase, logging_module: LoggingModuleBase) -> bool:
        pass

    @abstractmethod
    def send_input(self, stand: Stand, input: InputInfo) -> OutputInfo:
        pass
    
    @abstractmethod
    def send_raw(self, stand: Stand, input: InputInfo) -> Tuple[int, bytes]:
        pass
    
    