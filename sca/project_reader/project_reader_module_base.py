from abc import abstractmethod
from typing import Iterator

from ..core import ModuleBase

from .entity import FileInfo

class ProjectReaderModuleBase(ModuleBase):
    """Declares project reader moudle API.
    """
    
    @abstractmethod
    def get_file_iterator(self) -> Iterator[FileInfo]:
        pass
    
    @abstractmethod
    def get_file_info(self, id: str) -> FileInfo | None:
        pass
    
    @abstractmethod
    def read_file(self, file_info: FileInfo) -> bytes:
        pass

