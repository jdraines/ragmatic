

class PrinterBase:

    name = "base"
    
    def __init__(self):
        self.name = 'PrinterBase'

    def print(self, message):
        raise NotImplementedError