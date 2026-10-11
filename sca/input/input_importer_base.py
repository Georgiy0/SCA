from abc import ABC, abstractmethod
from typing import Dict, List

from .entity import InputInfo

class InputImporterBase(ABC):
    """Declares API for input importers.
    """
    
    @property
    @abstractmethod
    def Name(self) -> str:
        pass

    @abstractmethod
    def import_inputs(self, params: Dict[str,str]) -> List[InputInfo]:
        pass

