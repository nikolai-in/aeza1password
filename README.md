<h1 align="center">aeza1password</h1>
<blockquote align="center">
  Скрипт синхронизации серверов Aeza в 1Password
</blockquote>

<p align="center">
  <img src="https://github.com/nikolai-in/aeza1password/blob/master/aeza1password.png?raw=true" alt="Sublime's custom image"/>
</p>

## Дисклеймер

Это фан-проект, **НЕ** связанный ни с Aeza International Ltd, ни с 1Password.

## Использование

https://github.com/nikolai-in/aeza1password/assets/87097942/928d64f3-5d15-4755-adaa-498adf232c81

```bash
git clone && cd aeza1password && \
pip install -r requirements.txt
python aeza1password --help
```

```text
Usage: aeza1password [OPTIONS] [API_KEYS]...

  aeza1password — CLI tool for syncing servers from aeza.net to 1password

Options:
  --version  Show the version and exit.
  --dry-run  Dry run (don't actually create anything).
  --debug    Enable debug logging.
  -e, --env  Load configuration from .aeza1password.env file or environment.
  --help     Show this message and exit.
```

## Отказ от ответственности за использование товарных знаков

Все товарные знаки, логотипы и названия торговых марок являются собственностью соответствующих владельцев. Все названия компаний, продуктов и услуг, используемые на данном сайте, предназначены только для идентификации. Использование этих названий, торговых марок и брендов не подразумевает их одобрения.

- [Aeza.net](https://aeza.net/)
- [1Password](https://1password.com)
