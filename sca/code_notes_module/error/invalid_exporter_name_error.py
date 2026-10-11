from ...core import ScaError

class InvalidExporterNameError(ScaError):
    def __init__(self, name: str, *args):
        super().__init__(f"Invalid code notes exporter name '{name}'", *args)
        
        