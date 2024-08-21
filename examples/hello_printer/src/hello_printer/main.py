from argparse import ArgumentParser
from . import registry as reg


def get_args():
    parser = ArgumentParser()
    parser.add_argument("printer_type", type=str, help="Type of printer to use")
    return parser.parse_args()


def main():
    args = get_args()
    printer = reg.get_printer(args.printer_type)
    printer.print("Hello, World!")


if __name__ == "__main__":
    main()
    