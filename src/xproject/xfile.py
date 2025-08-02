import os
import zipfile
from typing import Literal


def compress_dir_path(
        dir_path: str,
        compress_type: Literal["zip"] = "zip"
) -> str | None:
    dir_path = os.path.abspath(dir_path)

    if not os.path.isdir(dir_path):
        return None

    valid_compress_type = ["zip"]
    if compress_type not in valid_compress_type:
        return None

    compress_file_path = os.path.join(
        os.path.dirname(dir_path), os.path.basename(dir_path) + "." + compress_type
    )

    if compress_type == "zip":
        with zipfile.ZipFile(compress_file_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_file_path = os.path.relpath(file_path, dir_path)
                    zf.write(file_path, arcname=rel_file_path)

        return compress_file_path

    return None


if __name__ == '__main__':
    print(compress_dir_path("."))
