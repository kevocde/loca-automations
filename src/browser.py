import time, os, re
from rich import print
from seleniumwire import webdriver
from selenium.webdriver.common.by import By



class Browser:
  BY_EQUIVALENCES = {"xpath": By.XPATH, 'id': By.ID, 'name': By.NAME, 'class': By.CLASS_NAME, 'tag': By.TAG_NAME, 'link': By.LINK_TEXT, 'partial_link': By.PARTIAL_LINK_TEXT, 'css': By.CSS_SELECTOR}

  def __init__(self, config: dict) -> None:
    self._config = config
    self._browser = self._load_browser_driver()


  def _load_browser_driver(self) -> None:
    options = webdriver.ChromeOptions()
    for key, value in self._config["general"]["browser"]["options"].items():
      setattr(options, key, self._parse_value(value))

    for key, value in self._config["general"]["browser"]["arguments"].items():
      if type(value) == bool and value:
        options.add_argument(f"--{key}")

    if "preferences" in self._config["general"]["browser"]:
      for key, value in self._config["general"]["browser"]["preferences"].items():
        self._config["general"]["browser"]["preferences"][key] = self._parse_value(value)

      options.add_experimental_option("prefs", self._config["general"]["browser"]["preferences"])

    return webdriver.Chrome(self._config["general"]["browser"]["driver"], chrome_options=options)


  def _wait_download_for(self, timeout: int, download_dir: str = None) -> None:
    seconds = 0
    download_complete = False

    if not download_dir:
      download_dir = self._parse_value(self._config["general"]["variables"]["download_dir"])

    to_ignore = len(re.findall(".crdownload", "|".join(os.listdir(download_dir))))

    while not download_complete and seconds < timeout:
      time.sleep(1)
      seconds += 1
      download_complete = not (len(re.findall(".crdownload", "|".join(os.listdir(download_dir)))) - to_ignore)


  def _parse_value(self, value: any) -> str:
    if type(value) != str:
      return value
    else:
      return re.sub(
        r"\$\{(\w+)\}",
        lambda match: self._config["general"]["variables"][match.group(1)] if match.group(1) in self._config["general"]["variables"] else "",
        value
      )


  def _check_for_errors(self) -> None:
    # Check ssl error
    if "ERR_CERT_AUTHORITY_INVALID" in self._browser.page_source:
      self._browser.find_element(By.ID, "proceed-link").click()

  def run(self):
    with self._browser as browser:
      for step_config in self._config["steps"]:
        url = [self._config["general"]["base_url"].strip("/"), step_config["uri"].lstrip("/")]
        url = self._parse_value('/'.join(url))

        print("[green]Running the step:[/green] {}".format(step_config["name"]))
        self._browser.get(url)
        self._check_for_errors()

        for action in step_config["actions"]:
          element = self._browser.find_element(self.BY_EQUIVALENCES[action["by"]["method"]], self._parse_value(action["by"]["value"]))

          if "type" in action:
            element.send_keys(self._parse_value(action["type"]))

          if "click" in action:
            element.click()

          if "submit" in action:
            element.submit()

          if "wait_download_for" in action:
            self._wait_download_for(action["wait_download_for"], (action["download_dir"] if "download_dir" in action else None))


if __name__ == "__main__":
  browser = Browser("/home/kevocde/Documents/Projects/BitsAmericas/TBO_Regional_2023/scripts/automatization/config/steps.yml")
  browser.run()
