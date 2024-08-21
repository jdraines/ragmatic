from typing import Type
from .printer_base import PrinterBase
from .caps_printer import CapsPrinter
from .lower_case_printer import LowerCasePrinter


_printers = {
    CapsPrinter.name: CapsPrinter,
    LowerCasePrinter: LowerCasePrinter
}

def register_printer(printer_cls: Type[PrinterBase]):
    _printers[printer_cls.name] = printer_cls

def get_printer(printer_type):
    if printer_type not in _printers:
        raise ValueError(f"Unknown printer type: {printer_type}")
    return _printers[printer_type]()
