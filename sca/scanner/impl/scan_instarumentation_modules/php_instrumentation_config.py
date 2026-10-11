from typing import List

from ....config import ConfigBase

class PhpInstrumentationConfig(ConfigBase):
    """PHP instrumentation modules config.
    
    Attributes:
        fetch_reports_locally (bool) - True for local reports fetching (via filesystem). False for remote reports download via HTTP(S)
        coverage_path (str) - path to coverage reports dir (if fetch_reports_locally == True)
        report_path (str) - path to reports dir (if fetch_reports_locally == True)
        php_implant_uri (str) - URI to a valid PHP request (for implant accessing if fetch_reports_locally == False)
    """
    
    fetch_reports_locally: bool
    coverage_path: str
    report_path: str
    php_implant_uri: str
    
    @staticmethod
    def default() -> 'PhpInstrumentationConfig':
        return PhpInstrumentationConfig(
            fetch_reports_locally=False,
            coverage_path="/path/to/cov/dir/",
            report_path="/path/ro/reports/dir/",
            php_implant_uri="/")
        
        