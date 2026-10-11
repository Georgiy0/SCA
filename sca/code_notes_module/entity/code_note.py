from pydantic import BaseModel
import json
import hashlib

from .code_note_importance import NoteImportance

class CodeNote(BaseModel):
    """Code note information.
    
    Attributes:
        file (str) - source code file path
        line (int) - line number
        importance (NoteImportance) - note importance
        note_type (str) - note type information (additional information)
        note (str) - note content
    """
    
    file: str
    line: int
    importance: NoteImportance
    note_type: str
    note: str

    def get_note_id(self) -> str:
        dump = self.model_dump()
        json_str = json.dumps(dump, sort_keys=True)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    @staticmethod
    def create(file: str, line: str, note_type: str, note: str, importance: NoteImportance) -> 'CodeNote':
        return CodeNote(
            file=file,
            line=line,
            note_type=note_type,
            importance=importance,
            note=note
        )
    
    @staticmethod
    def info(file: str, line: str, note_type: str, note: str) -> 'CodeNote':
        return CodeNote.create(file, line, note_type, note, NoteImportance.INFO)
    
    @staticmethod
    def low(file: str, line: str, note_type: str, note: str) -> 'CodeNote':
        return CodeNote.create(file, line, note_type, note, NoteImportance.LOW)
    
    @staticmethod
    def medium(file: str, line: str, note_type: str, note: str) -> 'CodeNote':
        return CodeNote.create(file, line, note_type, note, NoteImportance.MEDIUM)
    
    @staticmethod
    def high(file: str, line: str, note_type: str, note: str) -> 'CodeNote':
        return CodeNote.create(file, line, note_type, note, NoteImportance.HIGH)

