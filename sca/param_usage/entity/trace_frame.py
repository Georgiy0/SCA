from pydantic import BaseModel, TypeAdapter
from typing import List, Optional

class TraceFrame(BaseModel):
    file: Optional[str]
    line: Optional[int]
    
    
trace_frame_adapter = TypeAdapter(List[TraceFrame])