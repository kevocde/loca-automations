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


  def _wait_download_for(self, timeout: int, download_dir: str = None) -> set[str]:
    seconds = 0
    download_complete = False

    if not download_dir:
      download_dir = self._parse_value(self._config["general"]["variables"]["download_dir"])

    files_before = set(os.listdir(download_dir))
    current_files = set()
    to_ignore = len(re.findall(".crdownload", "|".join(files_before)))

    while not download_complete and seconds < timeout:
      time.sleep(1)
      seconds += 1
      current_files = set(os.listdir(download_dir))
      download_complete = not (len(re.findall(".crdownload", "|".join(current_files))) - to_ignore)

    return ["{}/{}".format(download_dir.rstrip("/"), file) for file in (current_files - files_before)]


  def _parse_value(self, value: any) -> str:
    if type(value) != str:
      return value
    else:
      return re.sub(
        r"\$\{(\w+)\}",
        lambda match: self._config["general"]["variables"][match.group(1)] if match.group(1) in self._config["general"]["variables"] else "",
        value
      )


  def get_computed(self, key: str, default: any = None) -> any:
    return self._config["general"]["computed"][key] if key in self._config["general"]["computed"] else default


  def set_computed(self, key: str, value: any) -> None:
    if not self._config["general"]["computed"]:
      self._config["general"]["computed"] = {}

    self._config["general"]["computed"][key] = value


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
            self.set_computed("downloaded_files", self._wait_download_for(action["wait_download_for"]))


if __name__ == "__main__":
  browser = Browser("/home/kevocde/Documents/Projects/BitsAmericas/TBO_Regional_2023/scripts/automatization/config/steps.yml")
  browser.run()
