from pydantic import BaseModel
from typing import Dict

from ...blob_store import BlobStoreBase
from ...config import ConfigModuleBase

from ..coverage_manager_module_base import CoverageManagerModuleBase
from ..entity import CoverageInfo, InputCoverage, CoverageStats
from ..error import InvalidCoverageExporterName

from .exporters import get_exporters
from .coverage_manager_config import CoverageManagerConfig

class InputToCoverageMapCache(BaseModel):
    """Cache of input coverage
    """
    
    cache: Dict[str,str] # input_id -> coverage_id


class CoverageManagerModule(CoverageManagerModuleBase):
    """Implements coverage manager.
    Per input coverage is stored via Object storage.
    Whole project coverage is updated when new coverage is added.
    """
    
    cCacheName = ".input-coverage-cache"
    cInputToCovCacheName = ".input-to-cov-cache"

    def __init__(self):
        super().__init__()
        self.__store: BlobStoreBase = None
        self.__input_coverage: InputCoverage = None
        self.__input_to_cov_map: InputToCoverageMapCache = None
        self.__exporters = get_exporters()
        self.__conifg: CoverageManagerConfig = None

    def init_module(self):
        super().init_module()
        config_module = self.Injector.get_module(ConfigModuleBase)
        if not config_module.has_config(CoverageManagerConfig):
            config_module.set_config(CoverageManagerConfig.default())
        self.__conifg = config_module.get_config(CoverageManagerConfig)

        self.__store = self.Injector.get_module(BlobStoreBase)
        self.__input_coverage = self.__store.load_or_set(InputCoverage, CoverageManagerModule.cCacheName,\
            InputCoverage(included_coverage={}, included_inputs={}, input_coverage={}))
        self.__input_to_cov_map = self.__store.load_or_set(InputToCoverageMapCache, CoverageManagerModule.cInputToCovCacheName,\
            InputToCoverageMapCache(cache={}))
    
    def deinit_module(self):
        self.__store.store(self.__input_coverage, CoverageManagerModule.cCacheName)
        self.__store.store(self.__input_to_cov_map, CoverageManagerModule.cInputToCovCacheName)
    
    def has_coverage(self, coverage_id):
        return self.__store.exists(CoverageInfo, coverage_id)
    
    def get_input_coverage(self, input_id):
        if input_id in self.__input_to_cov_map.cache:
            return self.__store.load(CoverageInfo, self.__input_to_cov_map.cache[input_id])
        return None
    
    def add_coverage(self, coverage_info):
        if self.has_coverage(coverage_info.coverage_id):
            return
        self.__store.store(coverage_info, coverage_info.coverage_id)
        self.__input_to_cov_map.cache[coverage_info.input_id] = coverage_info.coverage_id
        
        # merge input coverage
        for file, lines_info in coverage_info.coverage.items():
            if file not in self.__input_coverage.input_coverage:
                self.__input_coverage.input_coverage[file] = {}
            for line, cnt in coverage_info.coverage[file].items():
                if line not in self.__input_coverage.input_coverage[file]:
                    self.__input_coverage.input_coverage[file][line] = {}
                if len(self.__input_coverage.input_coverage[file][line]) == 0:
                    self.__input_coverage.input_coverage[file][line][coverage_info.input_id] = 1
        
        self.__input_coverage.included_coverage[coverage_info.coverage_id] = 1
        self.__input_coverage.included_inputs[coverage_info.input_id] = 1

    def get_exporters(self):
        return self.__exporters.values()
    
    def export_coverage(self, exporter_name, output_path):
        if exporter_name not in self.__exporters:
            raise InvalidCoverageExporterName(exporter_name, valid_names=list(self.__exporters.keys()))
        return self.__exporters[exporter_name].export(self.__input_coverage, output_path, self.__conifg.path_mappings)
    
    def get_input_ids_for_line(self, file, line):
        mapped_file = file
        for orig, proj in self.__conifg.path_mappings.items():
            if mapped_file.startswith(proj):
                mapped_file = mapped_file.replace(proj, orig)
                break
        print(mapped_file)
        if mapped_file in self.__input_coverage.input_coverage:
            strline = str(line)
            if strline in self.__input_coverage.input_coverage[mapped_file]:
                return list(self.__input_coverage.input_coverage[mapped_file][strline].keys())
        return []
    
    def get_stats(self):
        total_files = len(self.__input_coverage.input_coverage.keys())
        total_lines = 0
        for _, lines_dict in self.__input_coverage.input_coverage.items():
            total_lines += len(lines_dict)
        return CoverageStats(files_cnt=total_files, lines_cnt=total_lines)
        
        