from typing import Type, Dict, Any

from ..injector_base import InjectorBase
from ..error import ScaError

class Injector(InjectorBase):
    """Implements basic service locator (dictionary of services).
    """
    
    def __init__(self):
        super().__init__()
        self.__modules: Dict[Type, Any] = {}

    def get_module(self, module_type):
        if module_type in self.__modules:
            return self.__modules[module_type]
        return None

    def reg_module(self, iface, module):
        if iface in self.__modules:
            raise ScaError(f"Iface '{iface}' is already present in the injector")
        module.add_injector(self)
        self.__modules[iface] = module

    def get_modules(self):
        return self.__modules.values()

    def get_modules_of_type(self, modules_type):
        result = []
        for mtype, module in self.__modules.items():
            if issubclass(mtype, modules_type):
                result.append(module)
        return result
    
