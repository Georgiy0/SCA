from ...core import InjectorBase

from ..param_analyzer_module_base import ParamAnalyzerModuleBase

from .param_analyzer_module import ParamAnalyzerModule
from .value_providers import with_all_value_providers

def with_param_analyzer_module(injector: InjectorBase) -> InjectorBase:
    param_analyzer = ParamAnalyzerModule()
    injector.reg_module(ParamAnalyzerModuleBase, param_analyzer)
    
    with_all_value_providers(injector)
    return injector