from .printer_base import PrinterBase


class CapsPrinter(PrinterBase):
    
    name = "caps"

    def print(self, message):
        print(message.upper())