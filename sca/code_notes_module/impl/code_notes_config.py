from typing import Dict

from ...config import ConfigBase

class CodeNotesConfig(ConfigBase):
    """Code notes module configuration.
    
    Attributes:
        path_mappings (dict[str,str]) - path mappings between remote (target) file system and local file system
    """
    
    path_mappings: Dict[str,str]
    
    @staticmethod
    def default() -> 'CodeNotesConfig':
        return CodeNotesConfig(path_mappings={"/orig/path": "/mapped/path"})
    
    