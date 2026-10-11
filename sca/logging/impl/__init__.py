from ...core import InjectorBase

from ..logging_module_base import LoggingModuleBase

from .logging_module import LoggingModule

def with_logging(injector: InjectorBase) -> InjectorBase:
    lm = LoggingModule()
    injector.reg_module(LoggingModuleBase, lm)
    lm.init_module()
    return injector