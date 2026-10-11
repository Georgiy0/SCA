from abc import abstractmethod
from pydantic import BaseModel
from typing import Type, List

from ..core import ModuleBase

class BlobStoreBase(ModuleBase):
    """Declares object storage API for other modules
    """
    
    @abstractmethod
    def exists[T: BaseModel](self, item_type: Type[T], id: str) -> bool:
        pass

    @abstractmethod
    def load[T: BaseModel](self, item_type: Type[T], id: str) -> T:
        pass
    
    def load_or_set[T: BaseModel](self, item_type: Type[T], id: str, default: T) -> T:
        if not self.exists(item_type, id):
            self.store(default, id)
        return self.load(item_type, id)

    @abstractmethod
    def load_all[T: BaseModel](self, item_type: Type[T]) -> List[T]:
        pass

    @abstractmethod
    def store[T: BaseModel](self, item: T, id: str) -> bool:
        pass

