from argparse import ArgumentParser
from . import registry as reg


def get_args():
    parser = ArgumentParser()
    parser.add_argument("printer_type", type=str, help="Type of printer to use")
    parser.add_argument("--printer-import-path", "-i", type=str, help="Path to import printer from")
    return parser.parse_args()


def main():
    args = get_args()
    if args.printer_import_path:
        reg.import_and_register_printer(args.printer_import_path)
    printer = reg.get_printer(args.printer_type)
    printer.print("Hello, World!")


if __name__ == "__main__":
    main()
    