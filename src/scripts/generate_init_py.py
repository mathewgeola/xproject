import os
import sys

from rich.console import Console
from rich.syntax import Syntax

console = Console()


def generate_init_py(dir_path: str) -> int:
    dir_path = os.path.abspath(dir_path)
    if not os.path.isdir(dir_path):
        return 1

    py_file_names = [
        file_name for file_name in sorted(os.listdir(dir_path))
        if file_name.endswith(".py") and file_name not in ("__init__.py", "__main__.py")
    ]
    module_names = [os.path.splitext(py_file_name)[0] for py_file_name in py_file_names]
    if not module_names:
        return 0

    init_py_file_content_a = "\n".join(f"from . import {module_name}" for module_name in module_names)
    init_py_file_content_b = ",\n    ".join(f"'{module_name}'" for module_name in module_names)

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


def main():
    dir_path = sys.argv[1] if len(sys.argv) > 1 else "."
    sys.exit(generate_init_py(dir_path))
