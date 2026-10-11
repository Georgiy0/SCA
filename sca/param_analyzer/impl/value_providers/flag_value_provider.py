from typing import List

from ....input import InputInfo, InputParam, ParamType
from ....config import ConfigModuleBase

from ...param_value_provider_module_base import ParamValueProviderModuleBase

from .flag_value_provider_config import FlagValueProviderConfig

class FlagValueProvider(ParamValueProviderModuleBase):
    """Basic param value provider that uses a dictionary of values (flags).
    """
    
    @property
    def Name(self):
        return "flags"
    
    def init_module(self):
        config_module = self.Injector.get_module(ConfigModuleBase)
        self.__config = config_module.get_config_or_default(FlagValueProviderConfig,\
            FlagValueProviderConfig.default())

    def deinit_module(self):
        pass
    
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
        input_candidates: List[InputInfo] = []
        for pv in self.__config.flags:
            input_candidate = input.clone()
            input_candidate.params.append(InputParam(
                name=param_usage_info.param.name,
                param_type=param_usage_info.param.param_type,
                value=pv
            ))
            input_candidates.append(input_candidate)
        return input_candidates
            
