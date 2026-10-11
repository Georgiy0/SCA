from .http_scanner_module import HttpScannerModule

from ..scanner_module_base import ScannerModuleBase
from .scan_instarumentation_modules import with_scan_instrumentation_modules

from ...core import InjectorBase

def with_http_scaner(injector: InjectorBase) -> InjectorBase:
    http_scanner = HttpScannerModule()
    injector.reg_module(ScannerModuleBase, http_scanner)

    with_scan_instrumentation_modules(injector)
    return injector