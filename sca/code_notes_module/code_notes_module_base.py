from abc import abstractmethod
from typing import List

from ..core import ModuleBase

from .entity import CodeNote
from .code_notes_exporter_base import CodeNotesExporterBase

class CodeNotesModuleBase(ModuleBase):
    @abstractmethod
    def add_code_note(self, note: CodeNote) -> bool:
        pass

    @abstractmethod
    def get_exporters(self) -> List[CodeNotesExporterBase]:
        pass

    @abstractmethod
    def export(self, exporter_name: str, output: str) -> bool:
        pass

    