import os
from pathlib import Path
from typing import Type
from pydantic import BaseModel

from ...config import ConfigModuleBase

from ..blob_store_base import BlobStoreBase

from .file_blob_store_config import FileBlobStoreConfig


class FileBlobStore(BlobStoreBase):
    """Basic file storage implementation.
    Objects are stored in collections grouped by Python type.
    Each collection is stored in a seperate folder. 
    Each object is stored in a JSON-file.
    """
    
    cObjectFileExtension = "json"

    def __init__(self):
        super().__init__()
        self.__config: FileBlobStoreConfig = None

    def init_module(self):
        if not self.Injector.get_module(ConfigModuleBase).has_config(FileBlobStoreConfig):
            self.Injector.get_module(ConfigModuleBase).set_config(FileBlobStoreConfig.default())
        self.__config = self.Injector.get_module(ConfigModuleBase).get_config(FileBlobStoreConfig)
        if not os.path.isdir(self.__config.store_dir):
            os.mkdir(self.__config.store_dir)

    def deinit_module(self):
        pass
    
    def __get_item_collection_dir[T: BaseModel](self, item_type: Type[T], create: bool = False) -> str | None:
        collection_dir = os.path.join(self.__config.store_dir, item_type.__name__)
        if not os.path.isdir(collection_dir):
            if not create:
                return None
            else:
                os.mkdir(collection_dir)
        return collection_dir
        
    def __get_item_file_path[T: BaseModel](self, item_type: Type[T], id: str, create: bool = False) -> str | None:
        collection_dir = self.__get_item_collection_dir(item_type, create=create)
        if collection_dir is None:

            return None
        file_name_base = Path(id).name
        item_file_path = os.path.join(collection_dir, f"{file_name_base}.{FileBlobStore.cObjectFileExtension}")
        return item_file_path

    def exists(self, item_type, id):
        item_file_path = self.__get_item_file_path(item_type, id)
        return item_file_path is not None and os.path.isfile(item_file_path)

    def __load_item[T: BaseModel](self, item_type: Type[T], item_file_path: str) -> T:
        with open(item_file_path, 'rb') as fp:
            data = fp.read()
            return item_type.model_validate_json(data)

    def load(self, item_type, id):
        item_file_path = self.__get_item_file_path(item_type, id)
        if item_file_path is None or not os.path.isfile(item_file_path):
            return None
        return self.__load_item(item_type, item_file_path)

    def load_all(self, item_type):
        collection_dir = self.__get_item_collection_dir(item_type)
        if collection_dir is None:
            return []
        files = os.listdir(collection_dir)
        file_paths = [os.path.join(collection_dir, f) for f in files]
        result = []
        for item_file_path in file_paths:
            result.append(self.__load_item(item_type, item_file_path))
        return result
        
    def store(self, item, id):
        item_file_path = self.__get_item_file_path(type(item), id, create=True)
        with open(item_file_path, 'w', encoding='utf-8') as fp:
            json_str = item.model_dump_json(indent=4)
            fp.write(json_str)
            
            