#!/usr/bin/env python
"""aeza1password — CLI tool for syncing servers from aeza.net to 1password"""
import logging
import shutil
import subprocess  # nosec B404
import sys
from os import getenv

from dotenv import load_dotenv

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

AEZA_ENDPOINT = "https://my.aeza.net/api"


def check_for_op_cli():
    """Check for 1Password cli"""
    if not shutil.which("op"):
        logging.error(
            "1Password cli not found in path\n"
            + "Please install it https://1password.com/downloads/command-line/"
        )
        sys.exit(1)


def check_for_op_login():
    """Check for 1Password cli login"""
    if not subprocess.run(
        ["op", "account", "list"], capture_output=True
    ).stdout:  # nosec B603, B607
        logging.error(
            "1Password cli not logged in\n"
            + "Please run `op signin <your.1password.com>`"
        )
        sys.exit(1)


def run_checks():
    """Run checks to ensure op cli is ready"""
    check_for_op_cli()
    check_for_op_login()


def load_config() -> list:
    """Load configuration from .env file

    Returns:
        list: List of API keys
    """
    load_dotenv(".aeza1password.env")
    value = getenv("APIKEY")
    if type(value) is str:
        api_keys = value.split(",")
        logging.debug(f"Loaded {len(api_keys)} API keys")
        return api_keys
    logging.error("No API keys found in .aeza1password.env or environment")
    sys.exit(1)


def main():
    """Main entry point of the app"""
    logging.debug("Starting aeza1password")


if __name__ == "__main__":
    run_checks()
    load_config()
    main()
