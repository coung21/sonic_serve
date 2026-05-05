import argparse
from . import serve, check
from src.utils.logger import setup_logger

def main():
    parser = argparse.ArgumentParser(description="Zonic Inference Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    subparsers = parser.add_subparsers(dest="command", required=True)
    serve.add_subparser(subparsers)
    check.add_subparser(subparsers)

    args = parser.parse_args()
    
    setup_logger(args.debug)
    args.func(args)

if __name__ == "__main__":
    main()