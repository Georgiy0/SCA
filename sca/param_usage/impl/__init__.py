from ...core import InjectorBase

from ..param_usages_module_base import ParamUsagesModuleBase

from .param_usages_module import ParamUsagesModule

def with_param_usages_module(injector: InjectorBase) -> InjectorBase:
    param_usages = ParamUsagesModule()
    injector.reg_module(ParamUsagesModuleBase, param_usages)
    return injector