from enum import Enum

class InstrumentationCapability(str, Enum):
    COV = "cov" # coverage collection capability
    PARAM_USAGE = "params" # param usage collection capability

    