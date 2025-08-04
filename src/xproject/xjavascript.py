import subprocess
from typing import Any

import execjs
import py_mini_racer
import ujson


def _get_js_code(js_code: str | None = None, js_file_path: str | None = None) -> str:
    if js_code is None and js_file_path is None:
        raise ValueError(
            f"Either js_code: {js_code!r} or js_file_path: {js_file_path!r} must be provided"
        )
    if js_code is not None:
        return js_code
    if js_file_path is not None:
        with open(js_file_path, "r", encoding="utf-8") as f:
            js_code = f.read()
    return js_code


def execute_js_code_by_execjs(
        js_code: str | None = None,
        js_file_path: str | None = None,
        func_name: str | None = None,
        func_args: tuple[Any, ...] | None = None
) -> Any:
    js_code = _get_js_code(js_code, js_file_path)

    ctx = execjs.compile(js_code)
    if func_name is None:
        result = ctx.eval(js_code)
        return result
    if func_args is None:
        func_args = tuple()
    result = ctx.call(func_name, *func_args)
    return result


def execute_js_code_by_py_mini_racer(
        js_code: str | None = None,
        js_file_path: str | None = None,
        func_name: str | None = None,
        func_args: tuple[Any, ...] | None = None
) -> Any:
    js_code = _get_js_code(js_code, js_file_path)

    ctx = py_mini_racer.MiniRacer()
    result = ctx.eval(js_code)
    if func_name is None:
        return result
    if func_args is None:
        func_args = tuple()
    result = ctx.call(func_name, *func_args)
    return result


def execute_js_code_by_subprocess(
        js_code: str | None = None,
        js_file_path: str | None = None,
        func_args: tuple[dict[Any, Any], ...] | None = None,
) -> Any:
    js_code = _get_js_code(js_code, js_file_path)

    # js_code using `process.argv.slice(2)` to receive arguments
    func_args = ["node", "-e", js_code] + list(map(lambda x: ujson.dumps(x), func_args))
    process = subprocess.Popen(
        func_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    result = stdout.decode()
    return result
