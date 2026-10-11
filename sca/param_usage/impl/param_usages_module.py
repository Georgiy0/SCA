from typing import List, Dict, Tuple
from graphviz import Digraph

from ...core import ModuleBase
from ...config import ConfigModuleBase
from ...blob_store import BlobStoreBase
from ...code_notes_module import CodeNotesModuleBase, CodeNote, NoteImportance

from ..entity import ParamUsages, ParamUsageInfo, TraceFrame

from .param_usage_location_info import ParamUsageLocationInfo
from .param_usages_config import ParamUsagesConfig

class ParamUsagesModule(ModuleBase):
    """Implements param usage module.
    """
    
    cParamUsageCache = ".param-usage-cache"
    
    def __init__(self):
        super().__init__()
        self.__store: BlobStoreBase = None
        self.__config_module: ConfigModuleBase = None
        self.__code_notes_module: CodeNotesModuleBase = None
        self.__usages: ParamUsages = None
        self.__config: ParamUsagesConfig = None

    def init_module(self):
        super().init_module()
        self.__store = self.Injector.get_module(BlobStoreBase)
        self.__config_module = self.Injector.get_module(ConfigModuleBase)
        self.__code_notes_module = self.Injector.get_module(CodeNotesModuleBase)
        self.__config = self.__config_module.get_config_or_default(ParamUsagesConfig, ParamUsagesConfig.default())
        self.__usages = self.__store.load_or_set(ParamUsages, ParamUsagesModule.cParamUsageCache, ParamUsages(param_usages={}))
    
    def deinit_module(self):
        self.__store.store(self.__usages, ParamUsagesModule.cParamUsageCache)
    
    def add_param_usage(self, input_id, param, trace):
        if input_id not in self.__usages.param_usages:
            self.__usages.param_usages[input_id] = {}
        
        param_usage_info = ParamUsageInfo(
            analyzed=False,
            param=param,
            trace=trace
        )
        param_id = param_usage_info.get_hash()
        if param_id not in self.__usages.param_usages[input_id]:
            self.__usages.param_usages[input_id][param_id] = param_usage_info
            
    def get_param_usages(self):
        return self.__usages
    
    def get_ignore_param_trace_frames(self) -> List[str]:
        return self.__config.param_trace_ignore_frame
        
    def get_dropped_param_trace_frames(self) -> List[str]:
        return self.__config.param_trace_drop
    
    def __build_param_usage_trace_graph(self) -> ParamUsageLocationInfo:
        root = ParamUsageLocationInfo(location="__ROOT__", trace_depth=0, usages=[], children={})
                
        unique_param_usages: Dict[str, ParamUsageInfo] = {}
        for e in self.__usages.param_usages.values():
            for pu in e.values():
                key = f"{pu.trace[0].file}:{pu.trace[0].line}:{pu.param.param_type}:{pu.param.name}"
                if key not in unique_param_usages:
                    unique_param_usages[key] = pu
        
        root.usages = list(unique_param_usages.values())
        to_process: List[ParamUsageLocationInfo] = [root]
        
        while len(to_process):
            param_usage_location_info = to_process.pop()
            cur_depth = param_usage_location_info.trace_depth
            for param_usage_info in param_usage_location_info.usages:
                if len(param_usage_info.trace) <= cur_depth:
                    continue
                usage_location = f"{param_usage_info.trace[cur_depth].file}:{param_usage_info.trace[cur_depth].line}"
                if usage_location not in param_usage_location_info.children:
                    param_usage_location_info.children[usage_location] = ParamUsageLocationInfo(location=usage_location, trace_depth=cur_depth+1, usages=[], children={})
                param_usage_location_info.children[usage_location].usages.append(param_usage_info)
            to_process += [c for c in param_usage_location_info.children.values() if len(c.usages) > 1]
            
        return root
    
    def get_param_usage_traces_dot_graph(self):
        result = self.__build_param_usage_trace_graph()
        
        dot = Digraph(comment='Param usages')
        label = f"PARAM USAGES"
        dot.node(result.location.replace(":", "_"), label=label, shape='box')
        to_plot = [(result, c) for c in result.children.values()]
        while to_plot:
            parent, current = to_plot.pop()
            children = current.children.values()
            param_usages = current.usages
            if len(children) == 0:
                continue
            if len(children) < 2 and len(param_usages) < 3:
                continue
            location = current.location.split(":")
            param_types = list(set([pu.param.param_type for pu in current.usages]))
            param_types_used = ','.join(param_types)
            label = f"file: {location[0]}\nline: {location[1]}\ncall sites: {len(children)}\nparam usages: {len(param_usages)}\nparam types: {param_types_used}"
            dot.node(current.location.replace(":", "_"), label=label, shape='box')
            
            if parent:
                dot.edge(parent.location.replace(":", "_"), current.location.replace(":", "_"))
            
            if len(children) < 2:
                continue
            for child in children:
                to_plot.append((current, child))
        
        return dot.source
    
    def get_param_getter_wrapper_candidates(self):
        param_usage_trace_graph = self.__build_param_usage_trace_graph()
        
        to_walk = [(param_usage_trace_graph, c) for c in param_usage_trace_graph.children.values()]
        wrapper_candidates: Dict[str,List[str]] = {}
        while to_walk:
            _, current = to_walk.pop()
            children = current.children.values()
            param_usages = current.usages
            if len(children) == 0:
                continue
            if len(children) < 2 and len(param_usages) < 3:
                continue
            location = current.location
            param_types = list(set([pu.param.param_type for pu in current.usages]))
            wrapper_candidates[location] = param_types

            if len(children) < 2:
                continue
            for child in children:
                to_walk.append((current, child))
        
        return wrapper_candidates
    
    def __get_usage_location(self, trace: List[TraceFrame]) -> Tuple[str, int]:
        for frame in trace:
            loc = f"{frame.file}:{frame.line}"
            if loc not in self.__config.param_trace_ignore_frame:
                return frame.file, frame.line
        return None
    
    def add_param_usages_to_notes(self):
        cnt_added = 0
        for _, hash_to_param_usage in self.__usages.param_usages.items():
            for _, pu in hash_to_param_usage.items():
                file, line = self.__get_usage_location(pu.trace)
                if f"{file}:{line}" in self.__config.param_trace_drop:
                    continue
                note_text = f"[PARAM_USAGE] Param '{pu.param.name}' of type {pu.param.param_type}"
                if self.__code_notes_module.add_code_note(CodeNote(
                    file=file,
                    line=line,
                    importance=NoteImportance.INFO,
                    note_type="PARAM_USAGE",
                    note=note_text)):
                    cnt_added += 1
        return cnt_added
    
    