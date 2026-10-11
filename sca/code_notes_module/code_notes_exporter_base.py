from abc import ABC, abstractmethod
from typing import List, Dict

from .entity import CodeNote

class CodeNotesExporterBase(ABC):
    @property
    @abstractmethod
    def Name(self) -> str:
        pass

    @abstractmethod
    def export(self, path_mappings: Dict[str,str], notes: List[CodeNote], output: str) -> bool:
        pass

