from typing import List

from ...blob_store import BlobStoreBase

from ..input_manager_module_base import InputManagerModuleBase
from ..input_importer_base import InputImporterBase
from ..entity import InputInfo

from .uri_file_importer import UriFileImporter

class InputManagerModule(InputManagerModuleBase):
    """Implements input manager based on object storage.
    """
    
    def __init__(self):
        super().__init__()
        self.__store: BlobStoreBase = None

        self.__importers:  List[InputImporterBase] = [
            UriFileImporter()
        ]

    def init_module(self):
        self.__store = self.Injector.get_module(BlobStoreBase)

    def deinit_module(self):
        pass

    def get_inputs(self):
        inputs = self.__store.load_all(InputInfo)
        return inputs

    def get_importers(self):
        return self.__importers

    def import_inputs(self, importer, params):
        inputs = importer.import_inputs(params)
        for i in inputs:
            input_id = i.get_input_id()
            self.__store.store(i, input_id)

    def add_input(self, input_info):
        self.__store.store(input_info, input_info.get_input_id())
        
        