from typing import Dict

from ...coverage_exporter_base import CoverageExporterBase

from .lcov_exporter import LcovInfoExporter

def get_exporters() -> Dict[str, CoverageExporterBase]:
    lcov_info_exporter = LcovInfoExporter()
    exporters = {
        lcov_info_exporter.Name: lcov_info_exporter
    }
    return exporters