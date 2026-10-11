import os
import json
from typing import Dict

from ..config_module_base import ConfigModuleBase
from ..config_base import ConfigBase
from ..error import MissingConfigError

class FileConfigModule(ConfigModuleBase):
    """Implementation of single file configuration storage.
    Configuration is stored in JSON.
    Module configs are stored as seperate JSON-object in JSON-dictionary (__raw_config).
    """
    
    def __init__(self, config_path: str):
        super().__init__()
        self.__initialzied = False
        self.__config_path = config_path
        self.__raw_config: Dict[str, dict] = {}
        self.__config: Dict[str, ConfigBase] = {}

    def __load_config(self) -> Dict[str, dict]:
        with open(self.__config_path, 'rb') as fp:
            self.__raw_config = json.load(fp)

    def __dump_config(self) -> None:
        for name, config in self.__config.items():
            self.__raw_config[name] = config.model_dump()
        with open(self.__config_path, 'w', encoding='utf-8') as fp:
            json.dump(self.__raw_config, fp, indent=4)

    def init_module(self):
        if self.__initialzied:
            return
        if not os.path.isfile(self.__config_path):
            self.__dump_config()
        self.__load_config()
        self.__initialzied = True

    def deinit_module(self):
        self.__dump_config()

    def get_config(self, config_type):
        config_name = config_type.__name__
        if config_name not in self.__config:
            if config_name not in self.__raw_config:
                raise MissingConfigError(config_type)
            config = config_type.model_validate(self.__raw_config[config_name])
            self.__config[config_name] = config
        return self.__config[config_name]

    def has_config(self, config_type):
        config_name = config_type.__name__
        return config_name in self.__config or config_name in self.__raw_config

    def set_config(self, config):
        self.__config[type(config).__name__] = config

