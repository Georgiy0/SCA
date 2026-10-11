from .core import get_injector

from .surfscan_module_base import SurfScanModuleBase

from .config import with_file_config, ConfigBase, ConfigModuleBase
from .logging import with_logging
from .blob_store import with_file_blob_store, BlobStoreBase
from .input import with_input_manager, InputManagerModuleBase, ParamType, InputInfo
from .scanner import with_http_scaner, ScannerModuleBase
from .coverage import with_coverage_manager, CoverageManagerModuleBase
from .param_analyzer import with_param_analyzer_module, ParamAnalyzerModuleBase
from .param_usage import with_param_usages_module, ParamUsagesModuleBase
from .code_notes_module import with_code_notes_module, CodeNotesModuleBase
from .project_reader import with_folder_project_reader_module

class SurfScanModule(SurfScanModuleBase):
    def __init__(self, config_file: str):
        super().__init__()
        get_injector().reg_module(SurfScanModuleBase, self)
        with_file_config(self.Injector, config_file)
        with_logging(self.Injector)
        with_file_blob_store(self.Injector)
        with_input_manager(self.Injector)
        with_http_scaner(self.Injector)
        with_coverage_manager(self.Injector)
        with_param_analyzer_module(self.Injector)
        with_param_usages_module(self.Injector)
        with_code_notes_module(self.Injector)
        with_folder_project_reader_module(self.Injector)
        
    def init(self) -> None:
        for module in self.Injector.get_modules():
            self.Logger.log_trace(f"Initializing module {type(module).__name__}")
            module.init_module()

    def deinit(self) -> None:
        for module in self.Injector.get_modules():
            module.deinit_module()

    def init_module(self):
        pass

    def deinit_module(self):
        pass

    def run(self) -> None:
        scanner = self.Injector.get_module(ScannerModuleBase)
        input_manger = self.Injector.get_module(InputManagerModuleBase)
        inputs = input_manger.get_inputs()
        cnt = 0
        total = len(inputs)
        for i in inputs:
            cnt += 1
            uri = i.get_param_of_type(ParamType.URI)
            print(f"[{cnt}/{total}] Processing input with uri '{uri}'")
            scanner.scan(i)
            
    def trigger_line(self, file: str, line: int) -> bool:
        cov_module = self.Injector.get_module(CoverageManagerModuleBase)
        input_ids = cov_module.get_input_ids_for_line(file, line)
        if len(input_ids) == 0:
            return False
        store = self.Injector.get_module(BlobStoreBase)
        input = store.load(InputInfo, input_ids[0])
        scanner = self.Injector.get_module(ScannerModuleBase)
        scanner.replay(input)
        return True

    @property
    def InputManger(self) -> InputManagerModuleBase:
        return self.Injector.get_module(InputManagerModuleBase)
    
    @property
    def CoverageManager(self) -> CoverageManagerModuleBase:
        return self.Injector.get_module(CoverageManagerModuleBase)

    @property
    def CodeNoteModule(self) -> CodeNotesModuleBase:
        return self.Injector.get_module(CodeNotesModuleBase)
    
    @property
    def ParamAnalyzerModule(self) -> ParamAnalyzerModuleBase:
        return self.Injector.get_module(ParamAnalyzerModuleBase)
    
    @property
    def ParamUsagesModule(self) -> ParamUsagesModuleBase:
        return self.Injector.get_module(ParamUsagesModuleBase)
    
    