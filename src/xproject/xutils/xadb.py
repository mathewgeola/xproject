import pandas as pd

from xproject.xcommand import SubprocessPopenResult, SubprocessRunResult, execute_cmd_code_by_subprocess_popen, \
    execute_cmd_code_by_subprocess_run
from xproject.xlogger import Logger, get_logger


class ADB:
    def __init__(self) -> None:
        self.logger: Logger | None = None

    def open_log(self) -> None:
        self.logger = get_logger()

    def close_log(self) -> None:
        self.logger = None

    def execute_cmd_code_by_subprocess_popen(self, cmd_code: str, encoding: str | None = None) -> SubprocessPopenResult:
        if self.logger is None:
            return execute_cmd_code_by_subprocess_popen(cmd_code, encoding=encoding)
        return execute_cmd_code_by_subprocess_popen(cmd_code, encoding=encoding, logger=self.logger)

    def execute_cmd_code_by_subprocess_run(self, cmd_code: str, encoding: str | None = None) -> SubprocessRunResult:
        if self.logger is None:
            return execute_cmd_code_by_subprocess_run(cmd_code, encoding=encoding)
        return execute_cmd_code_by_subprocess_run(cmd_code, encoding=encoding, logger=self.logger)

    def get_android_version(self) -> str:
        return self.execute_cmd_code_by_subprocess_run("adb shell getprop ro.build.version.release").text

    def get_android_sdk(self) -> str:
        return self.execute_cmd_code_by_subprocess_run("adb shell getprop ro.build.version.sdk").text

    def get_cpu_abi(self) -> str:
        return self.execute_cmd_code_by_subprocess_run("adb shell getprop ro.product.cpu.abi").text

    def set_reverse_tcp(self, local_port: int = 8888, remote_port: int = 8888) -> None:
        self.execute_cmd_code_by_subprocess_run(f"adb reverse tcp:{local_port} tcp:{remote_port}")

    def get_reverse_tcp_list(self) -> list[str]:
        lst = self.execute_cmd_code_by_subprocess_run("adb reverse --list").text.split("\n")
        return [i for i in lst if i]

    def clear_reverse_tcp(self, local_port: int = 8888) -> None:
        self.execute_cmd_code_by_subprocess_run(f"adb reverse --remove tcp:{local_port}")

    def set_global_http_proxy(self, host: str, port: int = 8888) -> None:
        http_proxy = f"{host}:{port}"
        self.execute_cmd_code_by_subprocess_run(f"adb shell settings put global http_proxy {http_proxy}")

    def get_global_http_proxy(self) -> str:
        return self.execute_cmd_code_by_subprocess_run("adb shell settings get global http_proxy").text

    def clear_global_http_proxy(self) -> None:
        self.execute_cmd_code_by_subprocess_run("adb shell settings delete global http_proxy")

    def get_process_names_df(self, process_name: str | None = None) -> pd.DataFrame:
        lines = self.execute_cmd_code_by_subprocess_run("adb shell ps -A").text.splitlines()
        df = pd.DataFrame(
            [line.split(maxsplit=len(lines[0].split()) - 1) for line in lines[1:]], columns=lines[0].split()
        )
        if process_name:
            df = df[df["NAME"].str.contains(process_name)]
        return df


if __name__ == '__main__':
    adb = ADB()

    adb.open_log()

    # print(adb.get_android_version())
    # print(adb.get_android_sdk())
    # print(adb.get_cpu_abi())

    # adb.set_reverse_tcp()
    # print(adb.get_reverse_tcp_list())
    # adb.clear_reverse_tcp()

    # adb.set_global_http_proxy("127.0.0.1", 8888)
    # print(adb.get_global_http_proxy())
    # adb.clear_global_http_proxy()

    adb.close_log()

    print(adb.get_process_names_df())
    # adb.get_process_names_df().to_excel("output.xlsx", index=False)
