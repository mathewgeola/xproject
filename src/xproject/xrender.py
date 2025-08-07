import os
from typing import Any

import jinja2

from xproject.xstring import camel_to_snake, snake_to_camel


class Render:
    @classmethod
    def render(
            cls,
            template_file_path: str | None = None,
            template_dir_path: str | None = None, template_file_name: str | None = None,
            render_data: dict[str, Any] | None = None,
            render_file_path: str | None = None
    ) -> str:
        if template_file_path is None and (template_file_name is None or template_dir_path is None):
            raise ValueError(
                f"Either template_file_path: {template_file_path!r} or "
                f"template_file_name: {template_file_name!r} and template_dir_path: {template_dir_path!r} "
                f"must be provided"
            )

        if template_file_path is not None:
            template_file_path = os.path.abspath(template_file_path)

        if template_dir_path is not None:
            template_dir_path = os.path.abspath(template_dir_path)

        if render_data is None:
            render_data = dict()

        if template_file_path is not None:
            template_dir_path = os.path.dirname(template_file_path)
            template_file_name = os.path.basename(template_file_path)

        loader = jinja2.FileSystemLoader(searchpath=template_dir_path)
        env = jinja2.Environment(loader=loader)
        env.filters["camel_to_snake"] = camel_to_snake
        env.filters["snake_to_camel"] = snake_to_camel
        template = env.get_template(name=template_file_name)
        result = template.render(**render_data)

        if render_file_path is not None:
            with open(render_file_path, "w", encoding="utf-8") as file:
                file.write(result)

        return result
