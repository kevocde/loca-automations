import sys, pathlib, typer, yaml, gzip, shutil, os, subprocess

from browser import Browser
from rich import print
from yaml.loader import SafeLoader
from mergedeep import merge

app = typer.Typer()

def validate_path(path: str, message: str = "[red]The file doesn't exist[/red]") -> pathlib.Path:
  path = pathlib.Path(path)
  if not path.exists():
    print(message)
    sys.exit(1)

  return path.absolute()


def load_config_file(config_path: str):
  config_path = validate_path(config_path, "[red]The config file doesn't exist[/red]")

  with open(config_path, "r") as stream:
    return yaml.load(stream, Loader=SafeLoader)


def download_backup(config_path: str, **variables):
  config = merge(load_config_file(config_path), {"general": {"variables": variables}})
  browser = Browser(config)
  browser.run()

  return browser.get_computed("downloaded_files")


def load_backup(site_path: str, file_path: str):
  site_path = validate_path(site_path, "[red]The site path doesn't exist[/red]")
  file_path = validate_path(file_path, "[red]The backup file doesn't exist[/red]")

  with gzip.open(file_path, "rb") as f_in:
    output_name = pathlib.Path(file_path).parent.joinpath("temp.mysql")
    with open(output_name, "wb") as f_out:
      shutil.copyfileobj(f_in, f_out)

  subprocess.call("cd {} && drush sql-drop -y > /dev/null 2>&1 && drush sql-cli < {} > /dev/null 2>&1 && drush cr > /dev/null 2>&1".format(site_path, output_name), shell=True)


@app.command("update:db")
def update_db(config: str = None, environment: str = "dev", countries: str = None):
  countries = countries.split(",") if countries else ["bo", "co", "gt", "hn", "ni", "pa", "py", "sv"]
  config = config if config else "./config.yaml"

  for country in countries:
    username = typer.prompt(f"Username for {country}")
    password = typer.prompt(f"Password for {country}", hide_input=True)
    site_path = typer.prompt(f"Enter the site path for {country}")

    downloaded_files = download_backup(
      pathlib.Path(config).absolute(),
      environment=environment,
      country=country,
      username=username,
      password=password
    )

    load_backup(site_path, downloaded_files.pop())


@app.command("describe")
def describe():
  print("This is a command to describe the app")

if __name__ == "__main__":
  app()
