from .printer_base import PrinterBase


class CapsPrinter(PrinterBase):
    
    name = "caps"

    def __init__(self):
        self.name = 'CapsPrinter'

    def print(self, message):
        print(message.upper())