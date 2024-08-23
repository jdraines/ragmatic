import importlib
from typing import Type
from .printer_base import PrinterBase
from .caps_printer import CapsPrinter
from .lower_case_printer import LowerCasePrinter


_printers = {
    CapsPrinter.name: CapsPrinter,
    LowerCasePrinter: LowerCasePrinter
}

def import_and_register_printer(printer_import_path: str):
    module_path, printer_name = printer_import_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    printer_cls = getattr(module, printer_name)
    register_printer(printer_cls)

def register_printer(printer_cls: Type[PrinterBase]):
    _printers[printer_cls.name] = printer_cls

def get_printer(printer_type):
    if printer_type not in _printers:
        raise ValueError(f"Unknown printer type: {printer_type}")
    return _printers[printer_type]()
