from pydantic import BaseModel
from typing import Dict

class InputCoverage(BaseModel):
    """Whole project coverage information.
    
    Attributes:
        included_coverage (dict) - included coverage ids
        included_inputs (dict) - included input ids
        input_coverage (dict) - whole project coverage (file -> line -> [input_id1, input_id2] -> hit (cnt))
    """
    
    included_coverage: Dict[str, int]
    included_inputs: Dict[str, int]
    input_coverage: Dict[str, Dict[str, Dict[str, int]]] # file -> line -> [input_id1, input_id2] -> hit (cnt)

