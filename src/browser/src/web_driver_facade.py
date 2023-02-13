import types

from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver import ChromeOptions, FirefoxOptions, EdgeOptions, IeOptions, WebKitGTKOptions
from selenium.webdriver import Chrome, Firefox, Edge, Ie, WebKitGTK, Safari
from selenium.webdriver.safari.options import Options as SafariOptions
from .config import Config, BrowserType
from .action_executor import ActionExecutor



class WebDriverFacade:
  EQUVALENCES = equivalences = {
    BrowserType.CHROME.value: [ChromeOptions, Chrome],
    BrowserType.FIREFOX.value: [FirefoxOptions, Firefox],
    BrowserType.EDGE.value: [EdgeOptions, Edge],
    BrowserType.IE.value: [IeOptions, Ie],
    BrowserType.SAFARI.value: [SafariOptions, WebKitGTK],
    BrowserType.WEBKITGTK.value: [WebKitGTKOptions, WebKitGTK]
  }


  def __init__(self, config: dict) -> None:
    self._config = Config(config)
    self._load_browser_props()
    self._action_executor = ActionExecutor(self._driver, self._config)


  def _load_browser_props(self):
    """Loads browser driver instance and options"""
    if self._config.get('general.browser.type') not in self.EQUVALENCES:
      raise Exception('Browser type not supported')
    else:
      options_class, driver_class = self.EQUVALENCES[self._config.get('general.browser.type')]
      self._options = self._create_options(options_class)
      self._driver = driver_class(self._config.get('general.browser.driver'), options=self._options)


  def _create_options(self, options_class):
    options = options_class()

    for opt_key, opt_value in self._config.get('general.browser.options', {}).items():
      if hasattr(options_class, opt_key):
        if callable(getattr(options_class, opt_key)):
          self._load_browser_method(options, opt_key, opt_value)
        else:
          setattr(options, opt_key, opt_value)

    return options


  def _load_browser_method(self, options, opt_key, opt_value) -> None:
    if isinstance(opt_value, list):
      for value in opt_value:
        if "key" in value and "activate" in value and value["activate"]:
          getattr(options, opt_key)("--{}".format(value["key"]))
        elif "key" in value and "value" in value:
          getattr(options, opt_key)(value["key"], value["value"])
        else:
          pass
    else:
      getattr(options, opt_key)(**opt_value)


  def _load_browser_options(self) -> None:
    equivalences = {
      BrowserType.CHROME.value: ChromeOptions,
      BrowserType.FIREFOX.value: FirefoxOptions,
      BrowserType.EDGE.value: EdgeOptions,
      BrowserType.IE.value: IeOptions,
      BrowserType.SAFARI.value: SafariOptions,
      BrowserType.WEBKITGTK.value: WebKitGTKOptions
    }

    if self._config.get('general.browser.type') not in equivalences:
      raise Exception('Browser type not supported')
    else:
      self._options = equivalences[self._config.get('general.browser.type')]()

      for opt_key, opt_value in self._config.get('general.browser.options', {}).items():
        if hasattr(self._options, opt_key):
          if callable(getattr(self._options, opt_key)):
            self._load_browser_method(opt_key, opt_value)
          else:
            self._load_browser_attribute(opt_key, opt_value)


  def run(self) -> None:
    self._action_executor.run()


  @property
  def driver(self) -> ArgOptions | Chrome | Firefox | Edge | Ie | WebKitGTK | Safari:
    return self._driver
