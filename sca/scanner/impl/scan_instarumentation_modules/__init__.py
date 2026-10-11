from ....core import InjectorBase

from .php_coverage_collection_instrumentation_module import PhpCoverageCollectionInstrumentationModule
from .php_params_collection_instrumentation_module import PhpParamsCollectionInstrumentationModule

def with_scan_instrumentation_modules(injector: InjectorBase):
    php_cov_module = PhpCoverageCollectionInstrumentationModule()
    php_params_module = PhpParamsCollectionInstrumentationModule()
    injector.reg_module(PhpCoverageCollectionInstrumentationModule, php_cov_module)
    injector.reg_module(PhpParamsCollectionInstrumentationModule, php_params_module)
        
