from .printer_base import PrinterBase


class LowerCasePrinter(PrinterBase):
    
        def __init__(self):
            self.name = 'QuietPrinter'
    
        def print(self, message):
            print(message.lower())
