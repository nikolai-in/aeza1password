#!/usr/bin/env python
"""aeza1password — CLI tool for syncing servers from aeza.net to 1password"""
import logging
import shutil
import subprocess  # nosec B404
import sys
from os import getenv

import click
import requests
from dotenv import load_dotenv

AEZA_ENDPOINT = "https://my.aeza.net/api"

AEZA_LOCATIONS = {
    "us": "🇺🇸",
    "at": "🇦🇹",
    "fr": "🇫🇷",
    "de": "🇩🇪",
    "nl": "🇳🇱",
    "se": "🇸🇪",
    "fi": "🇫🇮",
    "ru": "🇷🇺",
}


def op_check_for_cli():
    """Check for 1Password cli"""
    if not shutil.which("op"):
        logging.error(
            "1Password cli not found in path\n"
            + "Please install it https://1password.com/downloads/command-line/"
        )
        sys.exit(1)


def op_check_for_login():
    """Check for 1Password cli login"""
    if not subprocess.run(
        ["op", "account", "list"], capture_output=True
    ).stdout:  # nosec B603, B607
        logging.error(
            "1Password cli not logged in\n"
            + "Please run `op signin <your.1password.com>`"
        )
        sys.exit(1)


def op_check_for_vault(vault: str) -> bool:
    """Check for 1Password vault

    Args:
        vault (str): Vault to check for

    Returns:
        bool: True if vault exists, False if not
    """
    if not subprocess.run(
        ["op", "vault", "get", vault], capture_output=True
    ).stdout:  # nosec B603, B607
        logging.debug(f"1Password vault {vault} not found")
        return False
    logging.debug(f"1Password vault {vault} exists")
    return True


def op_create_vault(vault: str):
    """Create 1Password vault

    Args:
        vault (str): Vault to create

    Raises:
        Exception: If vault creation fails
    """
    if subprocess.run(  # nosec B603, B607
        ["op", "vault", "create", vault], capture_output=True
    ).stdout:
        logging.debug(f"1Password vault {vault} created")
    else:
        logging.error(f"1Password vault {vault} not created")
        raise Exception(f"1Password vault {vault} not created")


def new_user(user_name: str, user_password) -> list:
    """Create new user for server

    Args:
        user_name (str): Username
        user_password (str): Password

    Returns:
        list: List of user details
    """
    if not user_password:
        user_password = (
            subprocess.run(
                ["openssl", "rand", "-base64", "18"],  # nosec B603, B607
                capture_output=True,
            )
            .stdout.decode("utf-8")
            .strip()
        )
    user = [
        f"username={user_name}",
        f"password={user_password}",
    ]

    return user


def op_add_server(
    server: dict,
    user_name: str,
    user_password: str,
    create_user: bool = False,
    dry_run: bool = False,
):
    """Add server to 1Password

    Args:
        server (dict): Server to add
        user_name (str): Username
        user_password (str): Password
        create_user (bool): Create user in 1Password. Defaults to False.
        dry_run (bool): Dry run (don't actually create anything). Defaults to False.
    """
    ips = []
    for i, ip in enumerate(server["ips"]):
        ips.append(f"IPv4 {i}.ip address[URL]={ip['value']}")
        ips.append(f"IPv4 {i}.domain[URL]={ip['domain']}")

    ips.append(f"IPv6.ip address[URL]={server['ipv6'][0]['value']}")

    if create_user:
        user = new_user(user_name, user_password)
    else:
        user = []

    command = [
        "op",
        "item",
        "create",
        "--category=server",
        f"--title={server['name']} {AEZA_LOCATIONS[server['locationCode']]}",
        "--vault=aeza",
        f"ssh[URL]=ssh://{server['ip']}",
        f"Admin Console.admin console username[text]={server['parameters']['username']}",
        f"Admin Console.console password={server['secureParameters']['data']['password']}",
        f"Admin Console.billing panel URL[URL]=https://my.aeza.net/services/{server['id']}",
        "--tags=aeza1password",
    ]
    command += ips
    command += user

    if dry_run:
        logging.info(f"Dry run: {command}")
        return

    logging.debug(f"Dry run: {command}")

    subprocess.run(  # nosec B603, B607
        command,
        capture_output=True,
    )


def run_checks():
    """Run checks to ensure op cli is ready"""
    op_check_for_cli()
    op_check_for_login()


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


def aeza_get_services(api_key: str) -> dict:
    """Get services from aeza.net
     Make a GET call to AEZA_ENDPOINT + /services with X-API-KEY header and return JSON

    Args:
        api_key (str): API key to use

    Returns:
        dict: List of services
    """
    headers = {"X-API-KEY": api_key}
    response = requests.get(
        f"{AEZA_ENDPOINT}/services", headers=headers, timeout=5
    ).json()
    if response.get("error"):
        logging.error(f"Error getting services: {response['error']['message']}")
    return response


@click.command()
@click.version_option()
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Dry run (don't actually create anything)",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="Enable debug logging",
)
@click.option(
    "-e",
    "--env",
    is_flag=True,
    default=False,
    help="Load configuration from .env file or environment",
)
@click.argument("api_keys", nargs=-1)
def main(  # noqa C901
    dry_run: bool,
    debug: bool,
    env: bool,
    api_keys: list,
):
    """A CLI tool for syncing servers from aeza.net to 1password\f

    Args:
        dry_run (bool): Dry run (don't actually create anything)
        debug (bool): Enable debug logging
        env (bool): Load configuration from .env file or environment
        api_keys (list): List of API keys
    """
    logging.basicConfig(
        format="%(levelname)s:%(message)s",
        level=logging.DEBUG if debug else logging.INFO,
    )

    if env and api_keys:
        logging.error("Cannot use --env and pass API keys")
        sys.exit(1)

    logging.debug("Starting aeza1password")
    if env:
        api_keys = load_config()
        if not api_keys:
            logging.error("No API keys found")
            sys.exit(1)

    if not api_keys and not env:
        api_keys = click.prompt(
            "Please enter your API keys (comma separated)", type=str
        ).split(",")

    servers_total = []

    for i, api_key in enumerate(api_keys):
        logging.debug(f"Processing API key {i + 1}/{len(api_keys)}")
        services = aeza_get_services(api_key)
        if services.get("error"):
            logging.info(f"Skipping API key {i + 1} due to error")
            continue
        servers_i = [
            item
            for item in services["data"]["items"]
            if item["product"]["type"] == "vps"
        ]
        if len(servers_i) == 0:
            logging.warning(f"No servers found for API key {i + 1}")
        logging.info(f"Found {len(servers_i)} servers for API key {i + 1}")
        servers_total += servers_i

    if not servers_total:
        logging.error("No servers found")
        sys.exit(1)

    logging.info(
        f"Found {len(servers_total)} servers in total for {len(api_keys)} API keys"
    )

    if not op_check_for_vault("aeza") and not dry_run:
        op_create_vault("aeza")

    for server in servers_total:
        logging.info(f"Processing server {server['name']}")
        op_add_server(
            server=server,
            create_user=False,
            dry_run=dry_run,
        )


if __name__ == "__main__":
    run_checks()
    main(prog_name="aeza1password")
