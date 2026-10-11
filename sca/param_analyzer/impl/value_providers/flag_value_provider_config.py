from typing import List

from ....config import ConfigBase

class FlagValueProviderConfig(ConfigBase):
    """Config for flag param value provider.
    
    Attributes:
        flags (list[str]) - list of flag values to substitute as param value.
    """
    
    flags: List[str]
    
    @staticmethod
    def default() -> 'FlagValueProviderConfig':
        return FlagValueProviderConfig(flags=["0", "1"])
    
    