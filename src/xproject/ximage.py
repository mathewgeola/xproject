import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import pillow_avif  # type: ignore
from PIL import Image


def image_to_jpg(
        image_file_path: str,
        /,
        jpg_file_path: str | None = None,
        quality: int = 100,
        keep_original: bool = False
) -> str | None:
    try:
        if jpg_file_path is None:
            image_file_prefix, _ = os.path.splitext(image_file_path)
            jpg_file_path = image_file_prefix + ".jpg"

        if image_file_path == jpg_file_path:
            return jpg_file_path

        jpg_dir_path = os.path.dirname(jpg_file_path)
        if not os.path.exists(jpg_dir_path):
            os.makedirs(jpg_dir_path, exist_ok=True)

        with Image.open(image_file_path) as image:
            if image.mode in ("RGBA", "LA"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode == "P":
                image.seek(0)  # image.n_frames
                image = image.convert("RGB")
            elif image.mode == "RGB":
                pass
            else:
                return None

            with NamedTemporaryFile(suffix=".jpg", delete=False, dir=jpg_dir_path) as ntf:
                temp_file_path = ntf.name
                image.save(temp_file_path, "JPEG", quality=quality)
            os.replace(temp_file_path, jpg_file_path)

        if not keep_original:
            p = Path(image_file_path)
            if p.exists() and str(p.resolve()) == str(p.absolute()):
                os.remove(image_file_path)

        return jpg_file_path
    except Exception as e:  # noqa
        return None


if __name__ == '__main__':
    from xproject.xurl import url_to_file_path

    input_file_path = url_to_file_path(
        # "https://img.jslink.com/FILE41f4c4a5db4e4007b09ae2dd2e08d853.JPG"
        # "https://www.cnncmall.com/photos/std-commodity/202505/802ae6c95ce01f49f1f9dada51169fa3.gif"
        # "https://www.cnncmall.com/photos/std-commodity/202506/324119dde7a483b0c54fdf7b2a5cbc2d.JPG"
        # "https://www.cnncmall.com/photos/std-commodity/202506/d09b671afd9ef8d1ef7abc86acf9d021.png"
        "https://fsyuncai.oss-cn-beijing.aliyuncs.com/2025-08-20/FILE6042f63720014c76bb4473e28710ad63.jpg"
    )
    output_file_path = image_to_jpg(input_file_path, keep_original=False)
    print(f"{input_file_path} => {output_file_path}")
