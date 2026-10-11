from enum import Enum

class LogLevel(str, Enum):
    TRACE = "trace"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

    