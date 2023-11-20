#!/usr/bin/env python
"""aeza1password — CLI tool for syncing servers from aeza.net to 1password"""
import logging
import shutil
import subprocess  # nosec B404
import sys
from os import getenv
from typing import List

import click
import requests
from dotenv import load_dotenv

from aeza1password.utils import IP_address, Location, OperatingSystem, Server

AEZA_ENDPOINT = "https://my.aeza.net/api"


def log_error_and_exit(message: str):
    """Logs error and exits.

    Args:
        message (str): Error message.
    """
    logging.error(message)
    sys.exit(1)


def op_check_for_cli():
    """Check for 1Password cli.

    Tries to call op cli and exits if it is not found.
    """
    if not shutil.which("op"):
        log_error_and_exit(
            "1Password cli not found in path\n"
            + "Please install it https://1password.com/downloads/command-line/"
        )


def op_check_for_login():
    """Check for 1Password cli login.

    Logs error and exits if not logged in.
    """
    if not subprocess.run(
        ["op", "account", "list"], capture_output=True
    ).stdout:  # nosec B603, B607
        log_error_and_exit(
            "1Password cli not logged in\n"
            + "Please run `op signin <your.1password.com>`"
        )


def op_check_for_vault(vault: str) -> bool:
    """Check for 1Password vault.

    Args:
        vault (str): Vault to check for.

    Returns:
        bool: True if vault exists, False if not.
    """
    if not subprocess.run(
        ["op", "vault", "get", vault], capture_output=True
    ).stdout:  # nosec B603, B607
        logging.debug(f"1Password vault {vault} not found")
        return False
    logging.debug(f"1Password vault {vault} exists")
    return True


def op_create_vault(vault: str):
    """Create 1Password vault.

    Args:
        vault (str): Vault to create.

    Raises:
        Exception: If vault creation fails.
    """
    if subprocess.run(  # nosec B603, B607
        ["op", "vault", "create", vault], capture_output=True
    ).stdout:
        logging.debug(f"1Password vault {vault} created")
    else:
        logging.error(f"1Password vault {vault} not created")
        raise Exception(f"1Password vault {vault} not created")


def op_add_server(server: Server, dry_run: bool = False, vault: str = "aeza"):
    """Add server to 1Password.

    Args:
        server (Server): Server to add.
        dry_run (bool): Dry run (don't actually create anything). Defaults to False.
        vault (str): Vault to add server to. Defaults to "aeza".
    """
    command = server_to_op(server, vault)

    if dry_run:
        logging.info(f"Dry run: {command}")
        return

    logging.debug(f"Dry run: {command}")

    subprocess.run(  # nosec B603, B607
        command,
        capture_output=True,
    )


def server_to_op(server: Server, vault: str = "aeza") -> List[str]:
    """Convert server to 1Password item.

    Args:
        server (Server): Server to convert.
        vault (str): Vault to add server to. Defaults to "aeza".

    Returns:
        List[str]: List of 1Password cli arguments.
    """

    ip_addresses = []
    for i, ip in enumerate(server.ip_address):
        ip_addresses.append(f"IP addresses.ip address {i + 1}[text]={ip.address}")
        if ip.domain:
            ip_addresses.append(f"IP addresses.domain {i + 1}[text]={ip.domain}")

    return [
        "op",
        "item",
        "create",
        "--category=server",
        f"--title={server.name} {server.location.flag}",
        "--vault=aeza",
        f"URL=https://aeza.net/services/{server.service_id}",
        f"username={server.admin_username}",
        f"password={server.admin_password}",
        f"email[text]={server.email}",
        f"notesPlain=OS: {server.os}\nCPU: {server.cpu} cores\nRAM: {server.ram} GB\nStorage: {server.storage} GB\n",
        "--tags=aeza,aeza1password,iterm2",
    ] + ip_addresses


def run_checks():
    """Run checks to ensure op cli is ready."""
    op_check_for_cli()
    op_check_for_login()


def load_config() -> list:
    """Load configuration from .env file.

    Returns:
        list: List of API keys.
    """
    load_dotenv(".aeza1password.env")
    value = getenv("APIKEY")
    if type(value) is str:
        api_keys = value.split(",")
        logging.debug(f"Loaded {len(api_keys)} API keys")
        return api_keys
    log_error_and_exit("No API keys found in .aeza1password.env or environment")


def aeza_get_services(api_key: str) -> dict:
    """Get services from aeza.net.
     Make a GET call to AEZA_ENDPOINT + /services with X-API-KEY header and return JSON.

    Args:
        api_key (str): API key to use.

    Returns:
        dict: List of services.
    """
    headers = {"X-API-KEY": api_key}
    try:
        response = requests.get(
            f"{AEZA_ENDPOINT}/services", headers=headers, timeout=5
        ).json()
        if response.get("error"):
            logging.error(f"Error getting services: {response['error']['message']}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error making API call: {str(e)}")
        response = {}
    return response


def setup_logging(debug: bool):
    """Setup logging.

    Args:
        debug (bool): Enable debug logging.
    """
    logging.basicConfig(
        format="%(levelname)s:%(message)s",
        level=logging.DEBUG if debug else logging.INFO,
    )


def load_api_keys(env: bool, api_keys: list) -> List[str]:
    """Load API keys from environment or prompt for them.

    Args:
        env (bool): Load configuration from .aeza1password.env file or environment.
        api_keys (list): List of API keys.

    Returns:
        List[str]: List of API keys.
    """
    if env and api_keys:
        log_error_and_exit("Cannot use --env and pass API keys")

    if env:
        api_keys = load_config()
        if not api_keys:
            log_error_and_exit("No API keys found")

    if not api_keys and not env:
        api_keys = click.prompt(
            "Please enter your API keys (comma separated)", type=str
        ).split(",")

    return api_keys


def process_servers(api_keys: list) -> List[Server]:
    """Process servers from aeza.net.

    Args:
        api_keys (list): List of API keys.

    Returns:
        List[Server]: List of servers.
    """
    servers_total = []
    for i, api_key in enumerate(api_keys):
        logging.debug(f"Processing API key {i + 1}/{len(api_keys)}")
        services = aeza_get_services(api_key)
        if services.get("error"):
            logging.info(f"Skipping API key {i + 1} due to error")
            continue
        server_on_api_key = []
        for item in services["data"]["items"]:
            if item["product"]["type"] != "vps":
                continue

            ips = [
                IP_address(address=ip["value"], domain=ip.get("domain", None))
                for ip in item["ips"] + item["ipv6"]
            ]

            server = Server(
                service_id=item["id"],
                name=item["name"],
                ip_address=ips,
                admin_username=item["parameters"]["username"],
                admin_password=item["secureParameters"]["data"]["password"],
                location=Location(item["locationCode"]),
                os=OperatingSystem(item["parameters"]["os"]),
                cpu=item["summaryConfiguration"]["cpu"]["count"],
                ram=item["summaryConfiguration"]["ram"]["count"],
                storage=item["summaryConfiguration"]["rom"]["count"],
                email=item["parameters"]["panelUsername"],
            )
            server_on_api_key.append(server)

        if len(server_on_api_key) == 0:
            logging.warning(f"No servers found for API key {i + 1}")
        logging.info(f"Found {len(server_on_api_key)} servers for API key {i + 1}")
        servers_total += server_on_api_key

    return servers_total


def add_servers(
    servers_total: list, dry_run: bool, api_keys: List[str] = None, vault: str = "aeza"
) -> None:
    """Add servers to 1Password.

    Args:
        servers_total (list): List of servers to add.
        dry_run (bool): Dry run (don't actually create anything).
        api_keys (List[str]): List of API keys. Defaults to None.
        vault (str): Vault to add servers to. Defaults to "aeza".
    """
    if not servers_total:
        log_error_and_exit("No servers found")

    logging.info(
        f"Found {len(servers_total)} servers in total for {len(api_keys)} API keys"
    )

    if not dry_run and not op_check_for_vault(vault):
        op_create_vault(vault)

    for server in servers_total:
        logging.info(f"Processing server {server.name}")
        op_add_server(
            server=server,
            dry_run=dry_run,
        )


@click.command()
@click.version_option()
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Dry run (don't actually create anything).",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Enable debug logging.",
)
@click.option(
    "-e",
    "--env",
    is_flag=True,
    default=False,
    help="Load configuration from .aeza1password.env file or env.",
)
@click.option(
    "-v",
    "--vault",
    default="aeza",
    help="Vault to add servers to.",
    metavar="",  # Hide default value in help cus it's ugly
)
@click.option(
    "--iterm2-pm",
    is_flag=True,
    default=False,
    help="Add servers logins to iTerm2 password manager instead.",
)
@click.help_option("-?", "-h", "--help")
@click.argument("api_keys", nargs=-1)
def main(
    dry_run: bool,
    debug: bool,
    env: bool,
    vault: str,
    api_keys: list,
):
    """aeza1password — CLI tool for syncing servers from aeza.net to 1password.
    Made by nikolai-in with love\f

    Args:
        dry_run (bool): Dry run (don't actually create anything).
        debug (bool): Enable debug logging.
        env (bool): Load configuration from .aeza1password.env file or environment.
        vault (str): Vault to add servers to.
        api_keys (list): List of API keys.
    """
    setup_logging(debug)
    api_keys = load_api_keys(env, api_keys)
    servers_total = process_servers(api_keys)
    add_servers(servers_total, dry_run, api_keys, vault)


if __name__ == "__main__":
    run_checks()
    main(prog_name="aeza1password")
