from ...core import ScaError

class InvalidSenderError(ScaError):
    def __init__(self, message, *args):
        super().__init__(message, *args)
        
        