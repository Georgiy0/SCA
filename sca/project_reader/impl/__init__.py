from ...core import InjectorBase

from ..project_reader_module_base import ProjectReaderModuleBase

from .foler_projecter_reader_module import FolderProjectReaderModule

def with_folder_project_reader_module(injector: InjectorBase) -> InjectorBase:
    fpr = FolderProjectReaderModule()
    injector.reg_module(ProjectReaderModuleBase, fpr)
    return injector