from .impl import Injector
from .module_base import ModuleBase
from .injector_base import InjectorBase
from .error import ScaError

def get_injector() -> InjectorBase:
    return Injector()