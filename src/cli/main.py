import argparse
from . import serve

def main():
    parser = argparse.ArgumentParser(description="Zonic Inference Server")
    subparsers = parser.add_subparsers(dest="command", required=True)
    serve.add_subparser(subparsers)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()