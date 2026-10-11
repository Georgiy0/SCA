from pydantic import BaseModel
from typing import Dict

class CoverageInfo(BaseModel):
    """Coverage information per input.
    
    Attributes:
        input_id (str) - input that triggeret the coverage
        coverage_id (str) - unique id (hash) of the coverage
        coverage (dict) - coverage information (file -> line -> hit (count))
    """
    
    input_id: str
    coverage_id: str
    coverage: Dict[str, Dict[str, int]]

