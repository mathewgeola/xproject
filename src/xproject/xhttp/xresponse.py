import re
from typing import Any

import ujson

from xproject.xjavascript import execute_js_code_by_py_mini_racer


def jsonp_to_json(jsonp: str) -> dict[str, Any]:
    func_name = re.match(r"(?P<func_name>jQuery.*?)\(\{.*\}\)\S*", jsonp).groupdict()["func_name"]
    js_code = f"function {func_name}(o){{return o}};function sdk(){{return JSON.stringify({jsonp})}};"
    json_str = execute_js_code_by_py_mini_racer(js_code, func_name="sdk")
    json_obj = ujson.loads(json_str)
    return json_obj
