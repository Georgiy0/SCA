from abc import abstractmethod
from typing import List, Dict

from ..core import ModuleBase

from .entity import InputInfo
from .input_importer_base import InputImporterBase

class InputManagerModuleBase(ModuleBase):
    """Declares API for managing inputs.
    """
    
    @abstractmethod
    def get_inputs(self) -> List[InputInfo]:
        pass

    @abstractmethod
    def get_importers(self) -> List[InputImporterBase]:
        pass

    @abstractmethod
    def import_inputs(self, importer: InputImporterBase, params: Dict[str,str]) -> bool:
        pass
    
    @abstractmethod
    def add_input(self, input_info: InputInfo) -> bool:
        pass
    
    