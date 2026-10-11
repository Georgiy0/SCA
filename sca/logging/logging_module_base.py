from abc import abstractmethod

from ..core import ModuleBase

from .log_level import LogLevel

class LoggingModuleBase(ModuleBase):
    """Declares logging API.
    """
    
    @abstractmethod
    def log(self, level: LogLevel, message: str) -> None:
        pass

    def log_trace(self, message: str) -> None:
        self.log(LogLevel.TRACE, message)

    def log_info(self, message: str) -> None:
        self.log(LogLevel.INFO, message)

    def log_warning(self, message: str) -> None:
        self.log(LogLevel.WARNING, message)

    def log_error(self, message: str) -> None:
        self.log(LogLevel.ERROR, message)

