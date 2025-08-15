import subprocess


def execute_cmd_code_by_subprocess(cmd_code: str, encoding: str = "utf-8") -> str | None:
    try:

        process = subprocess.Popen(
            cmd_code, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding=encoding
        )
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            result = stdout
        else:
            result = stderr

    except Exception:  # noqa
        result = None

    return result
