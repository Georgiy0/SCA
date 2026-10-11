from ...core import InjectorBase

from ..coverage_manager_module_base import CoverageManagerModuleBase

from .coverage_manager_module import CoverageManagerModule

def with_coverage_manager(injector: InjectorBase) -> InjectorBase:
    coverage_manager = CoverageManagerModule()
    injector.reg_module(CoverageManagerModuleBase, coverage_manager)
    return injector