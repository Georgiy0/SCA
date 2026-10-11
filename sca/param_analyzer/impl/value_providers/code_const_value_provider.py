from pydantic import BaseModel
from typing import Dict, List, Set
import re

from ....project_reader import ProjectReaderModuleBase
from ....blob_store import BlobStoreBase
from ....config import ConfigModuleBase
from ....input import InputInfo, InputParam, ParamType
from ....coverage import CoverageManagerModuleBase

from ...param_value_provider_module_base import ParamValueProviderModuleBase

from .code_const_value_provider_config import CodeConstValueProviderConfig

class CodeConstValueCache(BaseModel):
    """For storing already extracted constants (pre file)
    """
    cache: Dict[str, List[str]] # file id -> consts list


class CodeConstValueProvider(ParamValueProviderModuleBase):
    """Implements param value provider based on extraction of string literals
    form project source code files.
    
    Constans are extracted from relevent files (included in input coverage produced by the input that triggers param usage).
    """
    
    cCodeConstCacheName = ".code-const-values-cache"
    cStringLiteralRegex = re.compile(r'("(?:\\["\\]|[^"\\])*"|\'(?:\\[\'\\]|[^\'\\])*\')')
    
    def __init__(self):
        super().__init__()
        self.__reader: ProjectReaderModuleBase = None
        self.__store: BlobStoreBase = None
        self.__cov_module: CoverageManagerModuleBase = None
        self.__cache: CodeConstValueCache = None
        self.__config: CodeConstValueProviderConfig = None
        self.__re = None
    
    def init_module(self):
        self.__reader = self.Injector.get_module(ProjectReaderModuleBase)
        self.__store = self.Injector.get_module(BlobStoreBase)
        self.__cov_module = self.Injector.get_module(CoverageManagerModuleBase)
        
        self.__config = self.Injector.get_module(ConfigModuleBase).get_config_or_default(CodeConstValueProviderConfig, CodeConstValueProviderConfig.default())
        self.__cache = self.__store.load_or_set(CodeConstValueCache, CodeConstValueProvider.cCodeConstCacheName, CodeConstValueCache(cache={}))
        
        if self.__config.use_re:
            self.__re = re.compile(self.__config.re)
            

    def deinit_module(self):
        self.__store.store(self.__cache, CodeConstValueProvider.cCodeConstCacheName)

    @property
    def Name(self):
        return "code_consts"
    
    def __filter_const_candidate(self, const_candidate: str) -> bool:
        if not const_candidate.isascii():
            return False
        if self.__config.use_re and not self.__re.match(const_candidate):
            return False
        if len(const_candidate) < self.__config.min_const_length or len(const_candidate) > self.__config.max_const_length:
            return False
        if any(c in const_candidate for c in self.__config.forbidden_chars):
            return False
        return True
    
    def __extract_consts(self, data: str) -> List[str]:
        lines = data.split("\n")
        candidates: List[str] = []
        for l in lines:
            candidates += CodeConstValueProvider.cStringLiteralRegex.findall(l)
        candidates = [c.strip("'\"") for c in candidates]
        candidates = [c for c in candidates if self.__filter_const_candidate(c)]
        return candidates
    
    def __get_file_consts(self, file_path: str) -> List[str]:
        if file_path in self.__cache.cache:
            return self.__cache.cache[file_path]
        
        file_info = self.__reader.get_file_info(file_path)
        if file_info is None:
            self.Logger.log_warning(f"couldn't get file info for '{file_path}'")
            self.__cache.cache[file_path] = []
            return []
        try:
            data = self.__reader.read_file(file_info).decode("utf-8")
            consts = self.__extract_consts(data)
        
            self.__cache.cache[file_path] = consts
            return consts
        except Exception as e:
            self.Logger.log_error(f"failed to extract consts from file '{file_info}'")
            self.__cache.cache[file_path] = []
            return []
        
    def __cannot_mutate(self, param_type: ParamType) -> bool:
        return param_type in [
            ParamType.AUTH_DIGEST,
            ParamType.CREDS,
            ParamType.SOCKET_ADDR,
            ParamType.SOCKET_PORT
        ]

    def get_input_candidates(self, input, param_usage_info):
        if self.__cannot_mutate(param_usage_info.param.param_type):
            return []
        iid = input.get_input_id()
        cov = self.__cov_module.get_input_coverage(iid)
        if cov is None:
            self.Logger.log_warning(f"couldn't get coverage for iid '{iid}'")
            return []
        files_in_cov = list(cov.coverage.keys())
        if self.__config.only_param_usage_file:
            location = param_usage_info.trace[0].file
            files_in_cov = [f for f in files_in_cov if f.endswith(location)]
        consts: Set[str] = set()
        
        for f in files_in_cov:
            consts.update(self.__get_file_consts(f))
        
        input_candidates: List[InputInfo] = []
        for const_value in consts:
            input_candidate = input.clone()
            input_candidate.params.append(InputParam(
                name=param_usage_info.param.name,
                param_type=param_usage_info.param.param_type,
                value=const_value
            ))
            input_candidates.append(input_candidate)
        return input_candidates

