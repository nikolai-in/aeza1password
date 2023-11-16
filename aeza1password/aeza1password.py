#!/usr/bin/env python
"""aeza1password — CLI tool for syncing servers from aeza.net to 1password"""
import logging
from os import getenv

from dotenv import load_dotenv

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)


def load_config():
    """Load configuration from .env file"""
    load_dotenv(".aeza1password.env")
    value = getenv("APIKEY")
    if type(value) is str:
        api_keys = value.split(",")
        logging.debug(f"Loaded {len(api_keys)} API keys")


def main():
    """Main entry point of the app"""
    logging.debug("Starting aeza1password")


if __name__ == "__main__":
    load_config()
    main()
