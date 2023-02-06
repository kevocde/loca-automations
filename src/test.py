import browser, yaml, pathlib

from yaml.loader import SafeLoader


def load_configuration(path: str):
  path = pathlib.Path(path).absolute()

  with open(path, "r") as stream:
    return yaml.load(stream, Loader=SafeLoader)

if __name__ == "__main__":
  config = load_configuration("config/test-file.yml")
  browser = browser.WebDriverFacade(config)