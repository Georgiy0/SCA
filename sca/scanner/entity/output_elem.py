from pydantic import BaseModel
from typing import Optional

from .output_elem_type import OutputElemType

class OutputElem(BaseModel):
    elem_type: OutputElemType
    name: str
    value: Optional[str] = None

