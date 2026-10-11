from ...core import InjectorBase

from ..blob_store_base import BlobStoreBase

from .file_blob_store import FileBlobStore

def with_file_blob_store(injector: InjectorBase) -> InjectorBase:
    file_blob_store = FileBlobStore()
    injector.reg_module(BlobStoreBase, file_blob_store)
    return injector