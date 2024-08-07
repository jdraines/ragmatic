from argparse import ArgumentParser
from .caps_printer import CapsPrinter
from .lower_case_printer import LowerCasePrinter


_printers = {
    "caps": CapsPrinter,
    "lower": LowerCasePrinter
}


def get_args():
    parser = ArgumentParser()
    parser.add_argument("printer_type", type=str, help="Type of printer to use")
    return parser.parse_args()


def get_printer(printer_type):
    if printer_type not in _printers:
        raise ValueError(f"Unknown printer type: {printer_type}")
    return _printers[printer_type]()



def main():
    args = get_args()
    printer = get_printer(args.printer_type)
    printer.print("Hello, World!")


if __name__ == "__main__":
    main()
    