from selenium.webdriver.remote.webdriver import WebDriver
from .config import Config


class ActionExecutor:
  def __init__(self, driver: WebDriver, config: Config) -> None:
    self._driver = driver
    self._config = config


  def run(self):
    with self._driver as driver:
      for step_config in self._config.get('steps'):
        self._execute_step(driver, step_config)


  def _execute_step(self, driver: WebDriver, step_config: any) -> None:
    print("Executing step: {}".format(step_config["name"]))

    for action_config in step_config["actions"]:
      result = self.call_method_dynamically(
        driver,
        action_config["command"],
        (action_config["parameters"] if "parameters" in action_config else None)
      )

      if result and "handle" in action_config:
        for handle_key, handle_value in action_config["handle"].items():
          self.call_method_dynamically(result, handle_key, handle_value)


  @classmethod
  def call_method_dynamically(cls, object: any, command: str, parameters: any = None) -> any:
    if not object:
      raise Exception("Imposible call method on None object")

    if not callable(getattr(object, command)):
      raise Exception("Object {} has no method {}".format(object, command))

    params_type = type(parameters)

    if params_type in [str, int, float]:
      return getattr(object, command)(parameters)
    elif params_type == bool or params_type == type(None):
      return getattr(object, command)()
    elif params_type == list:
      return getattr(object, command)(*parameters)
    elif params_type == dict:
      return getattr(object, command)(**parameters)
    else:
      return None
