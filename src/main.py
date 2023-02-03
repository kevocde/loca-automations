import sys, pathlib, typer, yaml

from browser import Browser
from rich import print
from yaml.loader import SafeLoader
from mergedeep import merge

app = typer.Typer()

def _load_config_file(config_path: str):
  if not pathlib.Path(config_path).exists():
    print("[bold red]The config file doesn't exist[/bold red]")
    sys.exit(1)

  with open(config_path, "r") as stream:
    return yaml.load(stream, Loader=SafeLoader)


def download_backup(config_path: str, **variables):
  config = merge(_load_config_file(config_path), {"general": {"variables": variables}})
  browser = Browser(config)
  browser.run()


@app.command("update:db")
def update_db(config: str = None, environment: str = "dev", countries: str = None):
  countries = countries.split(",") if countries else ["bo", "co", "gt", "hn", "ni", "pa", "py", "sv"]
  config = config if config else "./config.yaml"

  for country in countries:
    username = typer.prompt(f"Username for {country}")
    password = typer.prompt(f"Password for {country}", hide_input=True)

    download_backup(
      pathlib.Path(config).absolute(),
      environment=environment,
      country=country,
      username=username,
      password=password
    )


@app.command("describe")
def describe():
  print("This is a command to describe the app")

if __name__ == "__main__":
  app()
