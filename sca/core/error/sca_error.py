

class ScaError(Exception):
    def __init__(self, message: str, *args):
        super().__init__(*args)
        self.__message = message

    @property
    def Message(self) -> str:
        return self.__message