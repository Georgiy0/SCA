from ...core import InjectorBase

from ..config_module_base import ConfigModuleBase

from .file_config_module import FileConfigModule

def with_file_config(injector: InjectorBase, config_path: str) -> InjectorBase:
    file_config_module = FileConfigModule(config_path)
    injector.reg_module(ConfigModuleBase, file_config_module)
    file_config_module.init_module()
    return injector