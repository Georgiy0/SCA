import logging
import sys

from ...config import ConfigModuleBase

from ..logging_module_base import LoggingModuleBase
from ..log_level import LogLevel
from ..logging_config import LoggingConfig

class LoggingModule(LoggingModuleBase):
    """Implements logging via Python logging module
    """
    
    def __init__(self):
        super().__init__()
        self.__initialized = False
    
    def to_python_log_level(self, level: 'LogLevel'):
        if level == LogLevel.TRACE:
            return logging.DEBUG
        elif level == LogLevel.INFO:
            return logging.INFO
        elif level == LogLevel.WARNING:
            return logging.WARNING
        elif level == LogLevel.ERROR:
            return logging.ERROR
        else:
            return logging.ERROR

    def init_module(self):
        if self.__initialized:
            return
        self.__initialized = True
        config_module = self.Injector.get_module(ConfigModuleBase)
        config = config_module.get_config_or_default(LoggingConfig, LoggingConfig.default())
        handlers = []
        if config.file is not None:
            handlers.append(logging.FileHandler(config.file, mode="a", encoding="utf-8"))
        if config.console:
            handlers.append(logging.StreamHandler(sys.stdout))
        logging.basicConfig(
            level=self.to_python_log_level(config.level),
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=handlers
        )
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    def deinit_module(self):
        pass

    def log(self, level, message):
        logging.log(self.to_python_log_level(level), message)

