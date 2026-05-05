import argparse
from src.config.loader import load_config
from src.api.server import create_app
import uvicorn

def add_subparser(subparsers):
    serve_parser = subparsers.add_parser("serve", help="start the inference server")
    serve_parser.add_argument("--config", type=str, default=None, help="Path to config file")
    serve_parser.set_defaults(func=run_server)
    
def run_server(args):
    config = load_config(args.config)
    app = create_app(config)
    uvicorn.run(app, host=config.server.host, port=config.server.port)