<h1 align="center">aeza1password</h1>
<blockquote align="center">
  CLI tool for syncing servers from aeza.net to 1password
</blockquote>

<p align="center">
  <img src="https://github.com/nikolai-in/aeza1password/blob/master/aeza1password.png?raw=true" alt="Sublime's custom image"/>
</p>

## Usage/Examples

```bash
git clone && cd aeza1password && \
pip install -r requirements.txt
python aeza1password --help
```

```text
Usage: aeza1password [OPTIONS] [API_KEYS]...

  A CLI tool for syncing servers from aeza.net to 1password

Options:
  --version      Show the version and exit.
  --create-user  Create new server user in 1Password
  --dry-run      Dry run (don't actually create anything)
  --debug        Enable debug logging
  -e, --env      Load configuration from .env file or environment
  --help         Show this message and exit.
```

## Trademark Disclaimer

All trademarks, logos and brand names are the property of their respective owners. All company, product and service names used in this website are for identification purposes only. Use of these names,trademarks and brands does not imply endorsement.

- [Aeza.net](https://aeza.net/)
- [1Password](https://1password.com)
