from pydantic import BaseModel

class FileInfo(BaseModel):
    """File information.
    
    Attributes:
        id (str) - unique file id
        name (str) - file name
        ext (str) - file extension
    """
    
    id: str
    name: str
    ext: str
    
    