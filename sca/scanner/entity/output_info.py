from pydantic import BaseModel, TypeAdapter
from typing import List, Dict
import json
import hashlib

from ...core import ScaError

from .output_elem import OutputElem
from .output_elem_type import OutputElemType

output_elem_type_adapter = TypeAdapter(List[OutputElem])

class OutputInfo(BaseModel):
    """Represents information from target project that resulted from input processing.
    """
    
    elements: List[OutputElem]
    
    def get_params_of_type(self, etype: OutputElemType) -> Dict[str, str]:
        return dict([(p.name, p.value) for p in self.elements if p.elem_type == etype])
    
    def get_param_of_type(self, etype: OutputElemType) -> str:
        elems = [p for p in self.elements if p.elem_type == etype]
        if len(elems) > 1:
            raise ScaError(f"More than one elem of type '{etype}' in otuput")
        if len(elems) == 0:
            raise ScaError(f"Missing param of type '{etype}' in otuput")
        return elems[0].value
    
    def get_output_id(self) -> str:
        list_of_elem_dicts = output_elem_type_adapter.dump_python(self.elements)
        json_str = json.dumps(list_of_elem_dicts, sort_keys=True)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
        
