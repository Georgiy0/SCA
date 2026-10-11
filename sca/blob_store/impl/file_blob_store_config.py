from ...config import ConfigBase

cDefaultStoreDir = ".store"

class FileBlobStoreConfig(ConfigBase):
    store_dir: str
    
    @staticmethod
    def default() -> 'FileBlobStoreConfig':
        return FileBlobStoreConfig(store_dir=cDefaultStoreDir)

    