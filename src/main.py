import sys, pathlib, typer, yaml, gzip, shutil, functools, subprocess

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
def update_db(config: str = None, environments: str = None, countries: str = None):
  countries = countries.split(",") if countries else ["bo", "co", "gt", "hn", "ni", "pa", "py", "sv"]
  environments = environments.split(",") if environments else ["dev", "qa", "stg"]
  config = config if config else "./config.yaml"

  for environment in environments:
    print(f"[bold green][Executing for {environment} environment ...][/bold green]")

    for country in countries:
      print(f"[bold blue][Downloading backup from {country} site ...][/bold blue]")

      username = typer.prompt(f"Username")
      password = typer.prompt(f"Password", hide_input=True)
      site_path = typer.prompt(f"Enter the site path")

      downloaded_files = download_backup(
        pathlib.Path(config).absolute(),
        environment=environment,
        country=country,
        username=username,
        password=password
      )

      load_backup(site_path, downloaded_files.pop())

      print("[bold blue][Done country][/bold blue]")

    print(f"[bold green][Done environment][/bold green]")

@app.command("auto-update:db")
def auto_update_db(sites_config: str, environments: str = None, countries: str = None):
  sites_config = validate_path(sites_config, "[red]The sites config file doesn't exist[/red]")
  sites_config = load_config_file(sites_config)
  general_config = load_config_file(sites_config["config_file"])

  if not environments:
    available_environments = [env["id"] for env in sites_config["environments"].values()]
  else:
    available_environments = environments.split(",")

  if not countries:
    available_countries = set([country["id"] for env in sites_config["environments"].values() for country in env["countries"].values()])
  else:
    available_countries = countries.split(",")

  for kenv, environment in sites_config["environments"].items():
    if environment["id"] in available_environments:
      print("[bold green][Updating {} environment ...][/bold green]".format(kenv))
      general_config = merge(
        general_config,
        {"general": {"base_url": environment["template_url"]}}
      )

      for kcountry, country in environment["countries"].items():
        if country["id"] in available_countries:
          print("[bold blue][Updating {} country ...][/bold blue]".format(kcountry))
          general_config = merge(
            general_config,
            {
              "general": {
                "variables": {
                  "username": country["variables"]["username"],
                  "password": country["variables"]["password"],
                  "country": country["id"],
                }
              }
            }
          )
          browser = Browser(general_config)
          browser.run()
          load_backup(country["location"], browser.get_computed("downloaded_files").pop())
          print("[bold blue][Country updated][/bold blue]")

      print(f"[bold green][Environment updated][/bold green]")


@app.command("describe")
def describe():
  print("This is a command to describe the app")

if __name__ == "__main__":
  app()
