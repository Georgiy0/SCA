from ...core import InjectorBase

from ..code_notes_module_base import CodeNotesModuleBase

from .code_notes_module import CodeNotesModule

def with_code_notes_module(injector: InjectorBase) -> InjectorBase:
    notes_module = CodeNotesModule()
    injector.reg_module(CodeNotesModuleBase, notes_module)
    return injector