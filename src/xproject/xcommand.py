import dataclasses
import re
import subprocess

from charset_normalizer import from_bytes

from xproject.xlogger import Logger


@dataclasses.dataclass(frozen=True)
class SubprocessPopenResult:
    content: bytes
    text: str


def execute_cmd_code_by_subprocess_popen(
        cmd_code: str,
        encoding: str | None = None,
        logger: Logger | None = None
) -> SubprocessPopenResult:
    if logger:
        logger.debug(f'''$ {cmd_code}''')

    process = subprocess.Popen(
        cmd_code, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    content = bytes()
    text = str()
    for line in process.stdout:
        content += line
        txt = "> "
        if encoding:
            txt += line.decode(encoding)
        elif best_match := from_bytes(line).best():
            txt += line.decode(best_match.encoding)
        else:
            txt += str(line)
        txt = txt.strip()
        if logger:
            logger.debug(txt)
        text += text
    _exit_code = process.wait()

    return SubprocessPopenResult(content, text)


@dataclasses.dataclass(frozen=True)
class SubprocessRunResult:
    result: subprocess.CompletedProcess
    content: bytes
    text: str


def execute_cmd_code_by_subprocess_run(
        cmd_code: str,
        encoding: str | None = None,
        logger: Logger | None = None
) -> SubprocessRunResult:
    if logger:
        logger.debug(f'''$ {cmd_code}''')

    result = subprocess.run(cmd_code, shell=True, capture_output=True)

    content = bytes()
    text = "> "
    for i in [result.stdout, result.stderr]:
        if i:
            content += i
            if encoding:
                text += i.decode(encoding)
            elif best_match := from_bytes(i).best():
                text += i.decode(best_match.encoding)
            else:
                text += str(i)
            text += "\n"
    text = re.sub(r"\r\n", "\n", text, re.DOTALL)
    text = re.sub(r"\n$", "", text, re.DOTALL)
    if logger:
        logger.debug(text)
    text = re.sub(r"^> ", "", text, re.DOTALL)

    return SubprocessRunResult(result, content, text)


if __name__ == '__main__':
    from xproject.xlogger import get_logger

    execute_cmd_code_by_subprocess_popen("ping www.baidu.com", "cp936", get_logger())
    execute_cmd_code_by_subprocess_run("ping www.baidu.com", "cp936", get_logger())
