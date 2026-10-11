from pydantic import BaseModel, TypeAdapter
from typing import List, Dict
import json
import hashlib

from ...core import ScaError

from .input_param import InputParam
adapter = TypeAdapter(List[InputParam])
from .param_type import ParamType

class InputInfo(BaseModel):
    """Stores input as a set of parameters (InputParam)
    """
    
    params: List[InputParam]
    
    def get_params_of_type(self, ptype: ParamType) -> Dict[str, str]:
        return dict([(p.name, p.value) for p in self.params if p.param_type == ptype])
    
    def get_param_of_type_or_default(self, ptype: ParamType, default: str | None = None) -> str | None:
        params = [p for p in self.params if p.param_type == ptype]
        if len(params) > 1:
            raise ScaError(f"More than one param of type '{ptype}' in input")
        if len(params) == 0:
            return None
        return params[0].value
    
    def get_param_of_type(self, ptype: ParamType) -> str:
        value = self.get_param_of_type_or_default(ptype)
        if value is None:
            raise ScaError(f"Missing param of type '{ptype}' in input")
        return value
    
    def get_param_or_default(self, ptype: ParamType, pname: str, default: str | None = None) -> str | None:
        params_of_type = self.get_params_of_type(ptype)
        if pname not in params_of_type:
            return default
        else:
            return params_of_type[pname]

    def has_param(self, ptype: ParamType, pname: str) -> bool:
        return len([p for p in self.params if p.param_type == ptype and p.name == pname]) > 0
    
    def get_input_id(self) -> str:
        list_of_param_dicts = adapter.dump_python(self.params)
        json_str = json.dumps(list_of_param_dicts, sort_keys=True)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def clone(self) -> 'InputInfo':
        list_of_param_dicts = adapter.dump_json(self.params)
        return InputInfo(
            params=adapter.validate_json(list_of_param_dicts)
        )
        
