from typing import Type

from ...core import ScaError

from ..config_base import ConfigBase

class MissingConfigError(ScaError):
    def __init__[CT: ConfigBase](self, config_type: Type[CT], *args):
        super().__init__(f"Missing config of type {config_type.__name__}", *args)
        
        