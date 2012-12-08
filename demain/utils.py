

class FlashMessage(str):
    def __new__(cls, message, clazz=None):
        self = super().__new__(cls, message)
        self.clazz = clazz
        return self