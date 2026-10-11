from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .injector_base import InjectorBase
    from ..logging import LoggingModuleBase

class ModuleBase(ABC):
    """Declares modules API with support of dependency injectin (via InjectorBase service locator).
    """
    
    def __init__(self):
        super().__init__()
        self.__injector = None
        self.__logger = None

    def add_injector(self, injector: 'InjectorBase') -> None:
        self.__injector = injector

    @property
    def Injector(self) -> 'InjectorBase':
        return self.__injector

    @abstractmethod
    def init_module(self) -> None:
        pass

    @abstractmethod
    def deinit_module(self) -> None:
        pass
    
    @property
    def Logger(self) -> 'LoggingModuleBase':
        if self.__logger is None:
            from ..logging import LoggingModuleBase
            self.__logger = self.Injector.get_module(LoggingModuleBase)
        return self.__logger