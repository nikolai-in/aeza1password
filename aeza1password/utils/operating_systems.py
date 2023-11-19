"""Module to convert aeza's OS id to OS names"""
from dataclasses import dataclass


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
