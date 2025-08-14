import os
import sys
from typing import Any, cast

from xproject.xrender import Render
from xproject.xstring import snake_to_camel


class RenderHandlerPy(Render):
    @classmethod
    def main(cls, *args: Any) -> None:
        render_file_path = os.path.abspath(
            args[0] if len(args) >= 1 else sys.argv[1] if len(sys.argv) > 1 else "handler.py"
        )
        class_name = snake_to_camel(os.path.splitext(os.path.basename(render_file_path))[0])
        render_data = dict(class_name=class_name)
        template_file_path = cast(str, os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "templates",
            os.path.splitext(os.path.basename(os.path.splitext(os.path.basename(__file__))[0]))[0],
            "handler.py.jinja2"
        ))
        sys.exit(cls.render(template_file_path, render_data=render_data, render_file_path=render_file_path))
