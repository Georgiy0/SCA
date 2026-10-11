from ...core import ScaError

class InputImportError(ScaError):
    def __init__(self, message, *args):
        super().__init__(message, *args)
    
    