from abc import abstractmethod
from typing import List

from ..core import ModuleBase

from .entity import CoverageInfo, CoverageStats
from .coverage_exporter_base import CoverageExporterBase

class CoverageManagerModuleBase(ModuleBase):
    """Coverage manager API for tracking per input code coverage.
    """
    
    @abstractmethod
    def has_coverage(self, coverage_id: str) -> bool:
        pass

    @abstractmethod
    def add_coverage(self, coverage_info: CoverageInfo) -> bool:
        pass
    
    @abstractmethod
    def get_input_coverage(self, input_id: str) -> CoverageInfo:
        pass

    @abstractmethod
    def get_exporters(self) -> List[CoverageExporterBase]:
        pass

    @abstractmethod
    def export_coverage(self, exporter_name: str, output_path: str) -> bool:
        pass
    
    @abstractmethod
    def get_input_ids_for_line(self, file: str, line: int) -> List[str]:
        pass
    
    @abstractmethod
    def get_stats(self) -> CoverageStats:
        pass