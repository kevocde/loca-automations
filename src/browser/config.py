import functools, re, json

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


  def _variable_resolver(self, data: str | dict) -> str | dict:
    was_dict = isinstance(data, dict)
    data = json.dumps(data) if was_dict else data
    data = re.sub(
      r"\$\{(\w+)\}",
      lambda match: self._raw_config["general"]["variables"][match.group(1)] if match.group(1) in self._raw_config["general"]["variables"] else "",
      data
    )
    return json.loads(data) if was_dict else data


  def get(self, key: str, default: any = None) -> any:
    key = self._variable_resolver(key)
    buffer = self._raw_config

    for key in key.split('.'):
      if key in buffer:
        buffer = buffer[key]
      else:
        return default if not isinstance(default, str) else self._variable_resolver(default)

    return self._variable_resolver(buffer)
