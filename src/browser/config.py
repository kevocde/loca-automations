import re, json

from enum import Enum
from mergedeep import merge



class BrowserType(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    IE = "ie"
    SAFARI = "safari"
    WEBKITGTK = "webkitgtk"



class Config:
  def __init__(self, raw_config: dict) -> None:
    self._raw_config = raw_config


  def variable_resolver(self, data: str | dict) -> str | dict:
    if not data:
      return None

    was_object = isinstance(data, dict) or isinstance(data, list)
    data = json.dumps(data) if was_object else data
    data = re.sub(
      r"\$\{(\w+)\}",
      lambda match: self._raw_config["general"]["variables"][match.group(1)] if match.group(1) in self._raw_config["general"]["variables"] else "",
      data
    )
    return json.loads(data) if was_object else data


  def get(self, key: str, default: any = None, variable_resolution: bool = True) -> any:
    default = default if not variable_resolution else self.variable_resolver(default)
    key = key if not variable_resolution else self.variable_resolver(key)
    buffer = self._raw_config if not variable_resolution else self.variable_resolver(self._raw_config)

    for key in key.split('.'):
      if key in buffer:
        buffer = buffer[key]
      else:
        return default

    return buffer
