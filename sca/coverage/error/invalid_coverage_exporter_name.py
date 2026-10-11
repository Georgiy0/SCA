from typing import List

from ...core import ScaError

class InvalidCoverageExporterName(ScaError):
    def __init__(self, exporter_name: str, valid_names: List[str], *args):
        self.__valid_names = valid_names
        super().__init__(f"Invalid coverage exporter name '{exporter_name}'. Available exporters:\n\t- {'\n\t- '.join(self.__valid_names)}", *args)
        
        