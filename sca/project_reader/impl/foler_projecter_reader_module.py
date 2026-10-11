from pathlib import Path
import os

from ...config import ConfigModuleBase

from ..project_reader_module_base import ProjectReaderModuleBase
from ..entity import FileInfo
from ..error import InvalidProjectFolderError

from .foler_project_config import FolderProjectConfig

class FolderProjectReaderModule(ProjectReaderModuleBase):
    """Implements project reader modules via direct access to project folder in local file system.
    """
    
    def __init__(self):
        super().__init__()
        self.__conifg: FolderProjectConfig = None
    
    def init_module(self):
        self.__conifg = self.Injector.get_module(ConfigModuleBase).get_config_or_default(FolderProjectConfig, FolderProjectConfig.default())
        if not os.path.isdir(self.__conifg.folder_path):
            raise InvalidProjectFolderError(f"Invalid project root directory path '{self.__conifg.folder_path}'.\nConfigure correct project path in project JSON file (FolderProjectConfig.folder_path)")
        
    def deinit_module(self):
        pass
    
    def __map_path(self, path: str) -> str:
        mapped_path = path
        for orig, target in self.__conifg.path_mappings.items():
            if mapped_path.startswith(orig):
                mapped_path = mapped_path.replace(orig, target)
        return mapped_path
        
    def __unmap_path(self, path: str) -> str:
        mapped_path = path
        for orig, target in self.__conifg.path_mappings.items():
            if mapped_path.startswith(target):
                mapped_path = mapped_path.replace(target, orig)
        return mapped_path

    def get_file_iterator(self):
        directory_path = Path(self.__conifg.folder_path)
        
        for path in directory_path.rglob("*"):
            if path.is_file():
                yield FileInfo(id=self.__map_path(path.absolute()), name=path.name, ext=path.suffix)
                
    def read_file(self, file_info):
        mapped_path = self.__map_path(file_info.id)
        with open(mapped_path, 'rb') as fp:
            return fp.read()
        
    def get_file_info(self, id):
        mapped_id = self.__map_path(id)
        if not mapped_id.startswith(self.__conifg.folder_path) or not os.path.isfile(mapped_id):
            return None
        path = Path(id)
        return FileInfo(id=str(path), name=path.name, ext=path.suffix)

    