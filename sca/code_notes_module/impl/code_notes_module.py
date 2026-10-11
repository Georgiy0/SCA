from typing import List

from ...blob_store import BlobStoreBase
from ...config import ConfigModuleBase

from ..code_notes_module_base import CodeNotesModuleBase
from ..error import InvalidExporterNameError
from ..entity import CodeNote

from .code_notes_list import CodeNotesList
from .code_notes_config import CodeNotesConfig
from .exporters import get_exporters

class CodeNotesModule(CodeNotesModuleBase):
    """Code notes module implementation based on object store.
    """
    
    cNotesListCache = ".code-notes-cache"

    def __init__(self):
        super().__init__()
        self.__store: BlobStoreBase = None
        self.__config_module: ConfigModuleBase = None
        self.__notes: CodeNotesList = None
        self.__exporters = get_exporters()
        self.__config: CodeNotesConfig = None

    def init_module(self):
        self.__store = self.Injector.get_module(BlobStoreBase)
        self.__config_module = self.Injector.get_module(ConfigModuleBase)

        if not self.__config_module.has_config(CodeNotesConfig):
            self.__config_module.set_config(CodeNotesConfig.default())
        self.__config = self.__config_module.get_config(CodeNotesConfig)

        if not self.__store.exists(CodeNotesList, CodeNotesModule.cNotesListCache):
            self.__notes = CodeNotesList(code_notes={})
            self.__store.store(self.__notes, CodeNotesModule.cNotesListCache)
        self.__notes = self.__store.load(CodeNotesList, CodeNotesModule.cNotesListCache)
    
    def deinit_module(self):
        self.__store.store(self.__notes, CodeNotesModule.cNotesListCache)
    
    def add_code_note(self, note):
        file = note.file
        line = note.line
        if file not in self.__notes.code_notes:
            self.__notes.code_notes[file] = {}
        strline = str(line)
        if strline not in self.__notes.code_notes[file]:
            self.__notes.code_notes[file][strline] = {}
        note_id = note.get_note_id()
        if note_id not in self.__notes.code_notes[file][strline]:
            self.__notes.code_notes[file][strline][note_id] = note
            return True
        return False
    
    def get_exporters(self):
        return self.__exporters.values()
    
    def export(self, exporter_name, output):
        if exporter_name not in self.__exporters:
            raise InvalidExporterNameError(exporter_name)
        all_notes: List[CodeNote] = []
        for file, line_to_notes in self.__notes.code_notes.items():
            for line, id_to_notes in line_to_notes.items():
                all_notes += list(id_to_notes.values())

        self.__exporters[exporter_name].export(self.__config.path_mappings, all_notes, output)
        return True

