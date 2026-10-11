from ....core import InjectorBase

from .flag_value_provider import FlagValueProvider
from .code_const_value_provider import CodeConstValueProvider

def with_all_value_providers(injector: InjectorBase) -> InjectorBase:
    with_flag_value_provider(injector)
    with_code_const_provider(injector)
    return injector

def with_flag_value_provider(injector: InjectorBase) -> InjectorBase:
    fv_provider = FlagValueProvider()
    injector.reg_module(FlagValueProvider, fv_provider)
    return injector

def with_code_const_provider(injector: InjectorBase) -> InjectorBase:
    ccvp = CodeConstValueProvider()
    injector.reg_module(CodeConstValueProvider, ccvp)
    return injector