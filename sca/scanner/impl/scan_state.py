from pydantic import BaseModel
from typing import Dict

class ScanState(BaseModel):
    """Helper class to store scan progress state.
    """
    
    scanned_inputs: Dict[str, int]

