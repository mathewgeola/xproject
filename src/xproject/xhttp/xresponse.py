import re
from typing import Any

import bs4
import httpx
import parsel
import requests
import ujson

from xproject.xjavascript import execute_js_code_by_py_mini_racer


def jsonp_to_json(jsonp: str) -> dict[str, Any]:
    func_name = re.match(r"(?P<func_name>jQuery.*?)\(\{.*\}\)\S*", jsonp).groupdict()["func_name"]
    js_code = f"function {func_name}(o){{return o}};function sdk(){{return JSON.stringify({jsonp})}};"
    json_str = execute_js_code_by_py_mini_racer(js_code, func_name="sdk")
    json_obj = ujson.loads(json_str)
    return json_obj


def response_to_text(response: httpx.Response | requests.Response) -> Any:
    return response.text


def response_to_xpath(response: httpx.Response | requests.Response) -> parsel.Selector:
    return parsel.Selector(response.text)


def response_to_json(response: httpx.Response | requests.Response) -> Any:
    jsn = ujson.loads(response.text)
    return jsn


def response_to_soup(response: httpx.Response | requests.Response) -> bs4.BeautifulSoup:
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    return soup
