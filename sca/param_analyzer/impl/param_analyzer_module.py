from typing import List, Tuple, Dict, Set

from ...blob_store import BlobStoreBase
from ...input import InputInfo, ParamType
from ...scanner import ScannerModuleBase
from ...coverage import CoverageManagerModuleBase
from ...input import InputManagerModuleBase, InputParam
from ...param_usage import ParamUsagesModuleBase, ParamUsageInfo, TraceFrame
from ...config import ConfigModuleBase

from ..param_analyzer_module_base import ParamAnalyzerModuleBase
from ..param_value_provider_module_base import ParamValueProviderModuleBase
from ..param_analyzer_observer_base import ParamAnalyzerStatus

from .param_analyzer_config import ParamAnalyzerConfig

class ParamAnalyzerModule(ParamAnalyzerModuleBase):
    """Implements param analyzis module.
    
    New inputs are generated via param value providers.
    If generated inputs provide new coverage (code coverage or new input param usages) they are stored for further analysis.
    """
    
    cParamUsageCache = ".param-usage-cache"

    def __init__(self):
        super().__init__()
        self.__store: BlobStoreBase = None
        self.__scanner: ScannerModuleBase = None
        self.__cov_manager: CoverageManagerModuleBase = None
        self.__input_manager: InputManagerModuleBase = None
        self.__param_usages_module: ParamUsagesModuleBase = None
        self.__value_providers: List[ParamValueProviderModuleBase] = []
        self.__conifg: ParamAnalyzerConfig = None

    def init_module(self):
        super().init_module()
        self.__store = self.Injector.get_module(BlobStoreBase)
        self.__scanner = self.Injector.get_module(ScannerModuleBase)
        self.__cov_manager = self.Injector.get_module(CoverageManagerModuleBase)
        self.__param_usages_module = self.Injector.get_module(ParamUsagesModuleBase)
        self.__input_manager = self.Injector.get_module(InputManagerModuleBase)
        self.__conifg = self.Injector.get_module(ConfigModuleBase).get_config_or_default(ParamAnalyzerConfig, ParamAnalyzerConfig.default())
        all_value_providers = self.Injector.get_modules_of_type(ParamValueProviderModuleBase)
        self.__value_providers = [vp for vp in all_value_providers if vp.Name in self.__conifg.providers]
    
    def deinit_module(self):
        pass
    
    def __param_to_key(self, param: InputParam) -> str:
        return f"{param.param_type}:{param.name}"

    def __has_new_param_usages(self, old: set[str], new: set[str]) -> bool:
        return len(new.difference(old)) > 0

    def __is_ignored(self, param: InputParam) -> bool:
        for ignore_type, ignore_names in self.__conifg.ignore_params.items():
            if param.param_type == ignore_type and param.name in ignore_names:
                return True
        return False
    
    def __get_usage_location(self, trace: List[TraceFrame]) -> str:
        for frame in trace:
            loc = f"{frame.file}:{frame.line}"
            if loc not in self.__param_usages_module.get_ignore_param_trace_frames():
                return loc
        return None

    def analyze(self, observer):
        usages = self.__param_usages_module.get_param_usages()
        new_inputs: List[InputInfo] = []
        total_pu = len(usages.param_usages)
        cnt_pu = 0
        cnt_total = 0
        cnt_tested = 0
        cnt_new = 0
        
        unique_param_usages = {}
        for input_id, valid_input_param_usages in usages.param_usages.items():
            for _, param_usage_info in valid_input_param_usages.items():
                param_usage_location = self.__get_usage_location(param_usage_info.trace)
                if param_usage_location in self.__param_usages_module.get_dropped_param_trace_frames():
                    self.Logger.log_info(f"Ignoring param usage at drop location (param {param_usage_info.param})")
                    continue
                key = f"{param_usage_location}:{param_usage_info.param.param_type}:{param_usage_info.param.name}"
                if key not in unique_param_usages:
                    unique_param_usages[key] = {
                        "input_ids": [],
                        "param_usages": [],
                        "analyzed": False
                    }
                unique_param_usages[key]["input_ids"].append(input_id)
                unique_param_usages[key]["param_usages"].append(param_usage_info)
                if param_usage_info.analyzed:
                    unique_param_usages[key]["analyzed"] = True
             
        cnt_new = 0
        
        unique_pu_not_analyzed = dict([(k, v) for (k, v) in unique_param_usages.items() if not v["analyzed"]])
        unique_pu_total = len(unique_pu_not_analyzed)
        cnt_pu = 0
        sorted_unique_locations_param = sorted(unique_pu_not_analyzed.items(), key=lambda p: len(p[1]["input_ids"]))
        for key, param_usage_info in sorted_unique_locations_param:
            cnt_pu += 1
            input_ids = param_usage_info["input_ids"]
            param_usages: List[ParamUsageInfo] = param_usage_info["param_usages"]
            param_usage: ParamUsageInfo = param_usages[0]
            if self.__is_ignored(param_usage.param):
                self.Logger.log_info(f"Ignoring param {param_usage.param}")
                continue
            param_key = self.__param_to_key(param_usage.param)
            valid_input = None
            valid_input_iid = None
            
            for iid in input_ids:
                input = self.__store.load(InputInfo, iid)
                input_params = set([self.__param_to_key(p) for p in input.params])
                
                if param_key not in input_params:
                    valid_input = input
                    valid_input_iid = iid
                    break
            
            if valid_input is None:
                continue
            
            new_inputs: List[Tuple[str, InputInfo]] = []
            for vp in self.__value_providers:
                added_inputs = vp.get_input_candidates(valid_input, param_usage) 
                new_inputs += [(valid_input_iid, ai) for ai in added_inputs]
                self.Logger.log_trace(f"adding {len(added_inputs)} new input for iid '{valid_input_iid}' via provider '{vp.Name}'")
                
            cnt_total = len(new_inputs)
            cnt_tested = 0
            
            seen_new_params: Dict[str,Set[str]] = {}
            while len(new_inputs) > 0:
                original_iid, ni = new_inputs.pop() 
                cnt_tested += 1
                if observer is not None:
                    if cnt_tested % observer.update_frequence() == 0:
                        observer.update_status(ParamAnalyzerStatus(
                            current_param=param_usage.param,
                            current_input=valid_input,
                            unique_params_total=unique_pu_total,
                            unique_params_cnt=cnt_pu,
                            new_candidates=cnt_total,
                            new_candidates_tested=cnt_tested,
                            new_cnt=cnt_new
                        ))
                ni_key = ni.get_input_id()
                if self.__store.exists(InputInfo, ni_key):
                    continue
                try:
                    report = self.__scanner.peek_scan(ni)
                    new_param_usages = set(report.param_usages.keys())
                    old_param_usages = set(usages.param_usages[original_iid].keys())
                    if original_iid in seen_new_params:
                        old_param_usages.update(seen_new_params[original_iid])
                    has_new_param_usages = self.__has_new_param_usages(old_param_usages, new_param_usages)
                    if not self.__cov_manager.has_coverage(report.coverage_id) or has_new_param_usages:
                        if original_iid not in seen_new_params:
                            seen_new_params[original_iid] = set()
                        seen_new_params[original_iid].update(new_param_usages)
                        self.__input_manager.add_input(ni)
                        self.__scanner.scan(ni)
                        cnt_new += 1
                except Exception as e:
                    self.Logger.log_warning(f"error trying new input '{ni.get_input_id()}'")
            for pu in param_usages:
                pu.analyzed = True
        return cnt_new

