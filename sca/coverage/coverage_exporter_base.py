from abc import ABC, abstractmethod
from typing import Dict

from .entity import InputCoverage

class CoverageExporterBase(ABC):
    """Basic type for coverage exporters.
    """
    
    @property
    @abstractmethod
    def Name(self) -> str:
        pass

    @abstractmethod
    def export(self, input_coverage: InputCoverage, output_path: str, path_mappings: Dict[str,str]) -> bool:
        pass