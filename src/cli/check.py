import argparse
import sys
from src.config.loader import load_config
from src.model.factory import create_model
from src.utils.logger import get_logger

logger = get_logger(__name__)

def add_subparser(subparsers):
    check_parser = subparsers.add_parser("check", help="Check yaml format is correct or not and test model loading")
    check_parser.add_argument("--config", type=str, required=True, help="Path to config file")
    check_parser.set_defaults(func=check_config)

def check_config(args):
    try:
        logger.info(f"Loading configuration from {args.config}")
        config = load_config(args.config)
        logger.info("Configuration format is valid.")
        
        logger.info("Attempting to load the model...")
        model = create_model(config.model)
        logger.info(f"Successfully loaded model: {model.__class__.__name__}")
        
    except Exception as e:
        logger.error(f"Error during check: {e}")
        sys.exit(1)
