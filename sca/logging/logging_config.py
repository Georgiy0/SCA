from ..config import ConfigBase

from .log_level import LogLevel

cDefaultLogFile = "sca.log"

class LoggingConfig(ConfigBase):
    """Loggin module configuration.
    
    Attributes:
        level (LogLevel) - log level
        file (str) - path to log file
        console (bool) - log to console output
    """
    
    level: LogLevel
    file: str | None = None
    console: bool

    @staticmethod
    def default() -> 'LoggingConfig':
        return LoggingConfig(level=LogLevel.WARNING, file=cDefaultLogFile, console=False)
    
    