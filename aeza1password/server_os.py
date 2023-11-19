"""Module to convert aeza's os id to names"""

import logging
import re

import requests

from aeza1password.__main__ import AEZA_ENDPOINT

OPERATING_SYSTEMS = {
    940: "Ubuntu 22.04",
    939: "Ubuntu 20.04",
    938: "Ubuntu 18.04",
    942: "CentOS 8 Stream",
    941: "CentOS 7",
    1991: "Debian 12",
    937: "Debian 11",
    936: "Debian 10",
    935: "Debian 9",
    929: "Windows Server 2012",
    930: "Windows Server 2016",
    931: "Windows Server 2019",
    1139: "Windows Server 2022",
    166: "FreeBSD 12",
    944: "Alma Linux 8",
    948: "Astra Linux CE",
    946: "Rocky Linux 8",
    947: "Rocky Linux 9",
}


def aeza_get_operating_systems(api_key: str) -> dict[int, str]:
    """Get OS dict from aeza.net

    Make a GET call to AEZA_ENDPOINT + /os with X-API-KEY header and return JSON

    Args:
        api_key (str): API key to use

    Returns:
        dict (int, str): List of operating systems

    """
    logging.debug("Getting operating systems from aeza.net")
    headers = {"X-API-KEY": api_key}
    response = requests.get(f"{AEZA_ENDPOINT}/os", headers=headers, timeout=5).json()
    if response.get("error"):
        logging.error(
            f"Error getting operating systems: {response['error']['message']}"
        )
    pattern = re.compile(r'\s*"id": (\d+),\s*\n\s*"name": "(.*)",')
    matches = pattern.findall(str(response))
    os_dict = {int(id_): name for id_, name in matches}
    return os_dict


def aeza_get_operating_system_from_id(id: int, api_key: str = None) -> str | None:
    """Get operating system name from aeza

    Args:
        id (int): Operating system id
        api_key (str): API key to use. Defaults to None.

    Returns:
        str: Operating system name
    """
    if id not in OPERATING_SYSTEMS:
        if api_key is None:
            return None
        if os_name := aeza_get_operating_systems(api_key).get(id, None):
            return os_name
        if not os_name:
            logging.error(f"Operating system {id} not found")
            return None
    return OPERATING_SYSTEMS[id]
