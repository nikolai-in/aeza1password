#!/usr/bin/env python
"""aeza1password — CLI tool for syncing servers from aeza.net to 1password"""
import logging
from os import getenv

from dotenv import load_dotenv

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

load_dotenv()
value = getenv("APIKEY")
if type(value) is str:
    api_keys = value.split(",")

logging.debug(f"API Keys: {api_keys}")
