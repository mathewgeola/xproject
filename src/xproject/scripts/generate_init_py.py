import os
import re
import sys
from typing import Any

from rich.console import Console
from rich.syntax import Syntax

from xproject.xlist import flatten_list

console = Console()


class GenerateInitPy:
    @staticmethod
    def _generate_init_py_by_dir_path(dir_path: str) -> int:
        dir_path = os.path.abspath(dir_path)
        if not os.path.isdir(dir_path):
            return 1

        if os.path.basename(dir_path) == "__pycache__":
            return 0

        module_names = []

        init_py_file_content_addition_a = None
        init_py_file_content_addition_b = None

        for file_name in sorted(os.listdir(dir_path)):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isfile(file_path):
                if file_name == "xproject.__init__.py":
                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            content = file.read()

                            init_py_file_content_addition_a = "\n".join(
                                sorted(
                                    re.findall(r"(from .*? import .*?)\n", content, re.DOTALL)
                                )
                            )
                            init_py_file_content_addition_b = ",\n    ".join([
                                f"\"{module_name}\"" for module_name in
                                sorted(
                                    flatten_list([i.split(", ") if ", " in i else i for i in
                                                  re.findall(r"from .*? import (.*?)\n", content, re.DOTALL)])
                                )
                            ])
                    except Exception:  # noqa
                        pass
                else:
                    if file_name.endswith(".py") and file_name not in ("__init__.py", "__main__.py"):
                        module_names.append(os.path.splitext(file_name)[0])
            elif os.path.isdir(file_path):
                if file_name != "__pycache__" and any(map(lambda x: x.endswith(".py"), os.listdir(file_path))):
                    module_names.append(file_name)

        if not module_names:
            return 0

        init_py_file_content_a = "\n".join(f"from . import {module_name}" for module_name in module_names)
        init_py_file_content_b = ",\n    ".join(f"\"{module_name}\"" for module_name in module_names)

        if init_py_file_content_addition_a is not None and init_py_file_content_addition_b is not None:
            init_py_file_content = f"""{init_py_file_content_addition_a}

{init_py_file_content_a}

__all__ = [
    {init_py_file_content_addition_b},

    {init_py_file_content_b},
]
"""
        else:
            init_py_file_content = f"""{init_py_file_content_a}

__all__ = [
    {init_py_file_content_b},
]
"""

        init_py_file_path = os.path.join(dir_path, "__init__.py")
        console.print(f"[bold green]{init_py_file_path}[/bold green]")

        with open(init_py_file_path, "w", encoding="utf-8") as f:
            f.write(init_py_file_content)
            syntax = Syntax(init_py_file_content, "python", theme="monokai", line_numbers=True)
            console.print(syntax)

        return 0

    @classmethod
    def _generate_init_py_by_root_dir_path(cls, root_dir_path: str) -> int:
        root_dir_path = os.path.abspath(root_dir_path)
        if not os.path.isdir(root_dir_path):
            return 1

        if os.path.basename(root_dir_path) == "__pycache__":
            return 0

        for root, dirs, files in os.walk(root_dir_path):
            if cls._generate_init_py_by_dir_path(root) != 0:
                return 1

        return 0

    @classmethod
    def main(cls, *args: Any) -> None:
        dir_path = os.path.abspath(args[0] if len(args) >= 1 else sys.argv[1] if len(sys.argv) > 1 else ".")
        sys.exit(cls._generate_init_py_by_root_dir_path(dir_path))
