from typing import Dict

from ...config import ConfigBase

class FolderProjectConfig(ConfigBase):
    """Folder project reader module configuration.
    
    Attributes:
        folder_path (str) - path to the folder with project source code.
        path_mappings (dict[str,str]) - dictionary with path mappings if the paths differ with the paths on debug host.
    """
    
    folder_path: str
    path_mappings: Dict[str,str]
    
    @staticmethod
    def default() -> 'FolderProjectConfig':
        return FolderProjectConfig(folder_path="/path/to/project/root/dir/", path_mappings={"/orig/dir": "/mapped/dir/"})
    
    