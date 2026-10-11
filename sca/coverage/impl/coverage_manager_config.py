from typing import Dict

from ...config import ConfigBase

class CoverageManagerConfig(ConfigBase):
    path_mappings: Dict[str,str]

    def default() -> 'CoverageManagerConfig':
        return CoverageManagerConfig(path_mappings={'/path/mapping/from': '/path/mapping/to'})
    
    