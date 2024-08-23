from .printer_base import PrinterBase


class LowerCasePrinter(PrinterBase):
    
    name = "lower"
    
    def print(self, message):
        print(message.lower())
