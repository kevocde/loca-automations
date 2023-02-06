import functools

from enum import Enum


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


  def get(self, key: str, default: any = None) -> any:
    buffer = self._raw_config

    for key in key.split('.'):
      if key in buffer:
        buffer = buffer[key]
      else:
        return default

    return buffer
