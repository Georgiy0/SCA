from .input_manager_module import InputManagerModule

from ..input_manager_module_base import InputManagerModuleBase

from ...core import InjectorBase

def with_input_manager(injector: InjectorBase) -> InjectorBase:
    input_manager = InputManagerModule()
    injector.reg_module(InputManagerModuleBase, input_manager)
    return injector