"""Utility functions and classes for aeza1password"""
from dataclasses import dataclass
from typing import List
from unicodedata import lookup


@dataclass
class OperatingSystem:
    """Dataclass for operating system

    Args:
        id (int): Operating system id
        name (str): Operating system name. Defaults to None.
    """

    id: int
    name: str = None

    def __post_init__(self):
        """Sets name from id

        If __OPERATING_SYSTEMS__ dict is out of date, you can update it by
        making a GET call to https://my.aeza.net/api/os with an api key and
        running a regex on the response

        pattern = re.compile(r'\\s*"id": (\\d+),\\s*\n\\s*"name": "(.*)",')
        matches = pattern.findall(str(response))
        os_dict = {int(id_): name for id_, name in matches}
        """
        __OPERATING_SYSTEMS__ = {
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

        self.name = __OPERATING_SYSTEMS__.get(self.id, None)

    def __str__(self):
        return self.name or str(self.id)


@dataclass
class Location:
    """Dataclass for location

    Args:
        name (str): Location name
        flag (str): Location flag in emoji.
                    Generated from name with unicode regional indicator symbols.
    """

    name: str
    flag: str = None

    def __post_init__(self):
        """Sets flag from name"""
        self.flag = "".join(
            [lookup(f"REGIONAL INDICATOR SYMBOL LETTER {c.upper()}") for c in self.name]
        )

    def __str__(self):
        """Returns name and flag

        Returns:
            str: name and flag

        Example:
            >>> location = Location("US)
            >>> print(location)
            US 🇺🇸
        """
        return f"{self.name} {self.flag}"


@dataclass
class IP_address:
    """Dataclass for IP address

    Args:
        address (str): IP address
        domain (str): Domain name. Defaults to None.
    """

    address: str
    domain: str = None


@dataclass
class Server:
    """Dataclass for server

    Args:
        service_id (int): Aeza service id
        name (str): Server name
        ip_address (List[IP_address]): List of IP addresses
        admin_username (str): Admin username
        admin_password (str): Admin password
        location (Location): Location
        os (str): Operating system
        cpu (str): CPU
        ram (str): RAM
        storage (str): Storage
    """

    service_id: int
    name: str
    ip_address: List[IP_address]
    admin_username: str
    admin_password: str
    location: Location
    os: str
    cpu: str
    ram: str
    storage: str
    email: str = None
