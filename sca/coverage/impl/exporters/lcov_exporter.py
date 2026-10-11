from typing import Dict

from ...coverage_exporter_base import CoverageExporterBase

class LcovInfoExporter(CoverageExporterBase):
    """Implements export to LCOV.info format.
    """
    
    @property
    def Name(self) -> str:
        return "lcov"

    def __write_lcov(self, path_mappings: Dict[str,str], name: str, output: str, coverage: Dict[str,Dict[str,Dict[str,int]]]) -> bool:
        with open(output, 'w', encoding='utf-8') as fp:
            fp.write(f"TN:{name}\n")
            for path, cov in coverage.items():
                mapped_path = path
                for mapping_from, mapping_to in path_mappings.items():
                    if path.startswith(mapping_from):
                        mapped_path = path.replace(mapping_from, mapping_to)
                        break
                fp.write(f"SF:{mapped_path}\n")
                for line, _ in cov.items():
                    fp.write(f"DA:{line},1\n")
                fp.write("end_of_record\n")
        return True
    
    def export(self, input_coverage, output_path, path_mappings):
        self.__write_lcov(path_mappings, "SurfScanCov", output_path, input_coverage.input_coverage)
        return True

    