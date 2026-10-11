from abc import ABC, abstractmethod
from typing import Type, List

from .module_base import ModuleBase

class InjectorBase(ABC):
    """Declares service locator API for modules.
    """
    
    @abstractmethod
    def get_module[T: ModuleBase](self, module_type: Type[T]) -> T:
        pass

    @abstractmethod
    def reg_module(self, iface: Type, module: ModuleBase) -> None:
        pass

    @abstractmethod
    def get_modules(self) -> List[ModuleBase]:
        pass

    @abstractmethod
    def get_modules_of_type[T: ModuleBase](self, modules_type: Type[T]) -> List[T]:
        pass