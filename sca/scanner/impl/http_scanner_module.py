from typing import List, Dict

from ...config import ConfigModuleBase
from ...blob_store import BlobStoreBase
from ...logging import LoggingModuleBase

from ..scanner_module_base import ScannerModuleBase
from ..error import InvalidSenderError
from ..scan_instrumentation_module_base import ScanInstrumentationModuleBase
from ..entity import ScanReport

from .scanner_config import ScannerConfig
from .requests_sender_base import HttpRequestsSender
from .request_senders import get_requset_senders
from .scan_state import ScanState

class HttpScannerModule(ScannerModuleBase):
    """Implements scanner module for web applications.
    """
    
    cScanStateCache = ".scan-state-cache"

    def __init__(self):
        super().__init__()
        self.__config: ScannerConfig = None
        self.__senders: Dict[str, HttpRequestsSender] = get_requset_senders()
        self.__sender: HttpRequestsSender = None
        self.__store: BlobStoreBase = None
        self.__instrumentation_modules: List[ScanInstrumentationModuleBase] = []
        self.__scan_state: ScanState = None

    def init_module(self):
        self.__store = self.Injector.get_module(BlobStoreBase)
        self.__config = self.Injector.get_module(ConfigModuleBase).get_config_or_default(ScannerConfig, ScannerConfig.default())
        if self.__config.sender_name not in self.__senders:
            self.__sender = None
        else:
            self.__sender = self.__senders[self.__config.sender_name]
            self.__sender.init_sender(self.Injector.get_module(ConfigModuleBase), self.Injector.get_module(LoggingModuleBase))
        all_instrumentation_modules = self.Injector.get_modules_of_type(ScanInstrumentationModuleBase)
        self.__instrumentation_modules = [m for m in all_instrumentation_modules if m.Name in self.__config.insturmentation_modules]

        if not self.__store.exists(ScanState, HttpScannerModule.cScanStateCache):
            self.__scan_state = ScanState(scanned_inputs={})
            self.__store.store(self.__scan_state, HttpScannerModule.cScanStateCache)
        self.__scan_state = self.__store.load(ScanState, HttpScannerModule.cScanStateCache)

    def deinit_module(self):
        self.__store.store(self.__scan_state, HttpScannerModule.cScanStateCache)
    
    def scan(self, input):
        if self.__sender is None:
            raise InvalidSenderError(f"invalid sender name in config '{self.__config.sender_name}'")

        input_id = input.get_input_id()
        if input_id in self.__scan_state.scanned_inputs:
            return
        
        instrumented_input = input.clone()

        for im in self.__instrumentation_modules:
            im.pre_send_action(input_id, instrumented_input, self.__sender, self.__config.stand)
        output = self.__sender.send_input(self.__config.stand, instrumented_input)
        for im in self.__instrumentation_modules:
            im.post_send_action(input_id, instrumented_input, output, self.__sender, self.__config.stand)
        self.__store.store(output, input_id)
        self.__scan_state.scanned_inputs[input_id] = 1

    def replay(self, input):
        if self.__sender is None:
            raise InvalidSenderError(f"invalid sender name in config '{self.__config.sender_name}'")

        output = self.__sender.send_input(self.__config.stand, input)

    def peek_scan(self, input, allowed_capabilities = None):
        if self.__sender is None:
            raise InvalidSenderError(f"invalid sender name in config '{self.__config.sender_name}'")
        
        instrumentation_modules = self.__instrumentation_modules
        if allowed_capabilities is not None:
            instrumentation_modules = [im for im in instrumentation_modules if len(set(im.Capabilities).difference(set(allowed_capabilities))) == 0]
            
        input_id = input.get_input_id()
        instrumented_input = input.clone()

        for im in instrumentation_modules:
            im.pre_send_action(input_id, instrumented_input, self.__sender, self.__config.stand)
        output = self.__sender.send_input(self.__config.stand, instrumented_input)
        scan_report = ScanReport()
        for im in instrumentation_modules:
            im.populate_scan_report(input_id, instrumented_input, output, scan_report, self.__sender, self.__config.stand)
        return scan_report

