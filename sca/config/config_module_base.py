from abc import abstractmethod
from typing import Type

from ..core import ModuleBase

from .config_base import ConfigBase

class ConfigModuleBase(ModuleBase):
    """Declares API for module configuration storage.
    """
    
    @abstractmethod
    def has_config[CT: ConfigBase](self, config_type: Type[CT]) -> bool:
        pass

    @abstractmethod
    def get_config[CT: ConfigBase](self, config_type: Type[CT]) -> CT:
        pass

    @abstractmethod
    def set_config[CT: ConfigBase](self, config: CT) -> None:
        pass
    
    def get_config_or_default[CT: ConfigBase](self, config_type: Type[CT], default: CT) -> CT:
        if not self.has_config(config_type):
            self.set_config(default)
        return self.get_config(config_type)

