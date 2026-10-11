from pydantic import BaseModel
from typing import Dict

from ..entity import CodeNote

class CodeNotesList(BaseModel):
    code_notes: Dict[str, Dict[str, Dict[str, CodeNote]]] # file -> line -> note_id -> note

    