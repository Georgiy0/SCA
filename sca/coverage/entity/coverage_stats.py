from pydantic import BaseModel

class CoverageStats(BaseModel):
    files_cnt: int
    lines_cnt: int
    
    