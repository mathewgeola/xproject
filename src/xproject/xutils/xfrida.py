from __future__ import annotations

import importlib
import lzma
import os
import pprint
import random
import re
import sys
import time
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING

from xproject.xcommand import SubprocessPopenResult, SubprocessRunResult, execute_cmd_code_by_subprocess_popen, \
    execute_cmd_code_by_subprocess_run
from xproject.xlogger import get_logger, Logger
from xproject.xnetwork import get_host
from xproject.xurl import url_to_file_path, get_furl_obj

if TYPE_CHECKING:
    import frida
    import _frida

    Frida = frida
    _Frida = _frida
else:
    Frida = object
    _Frida = object

frida: Frida | None = None
_frida: _Frida | None = None


@dataclass(frozen=True)
class FridaData:
    frida_server_xz_url: str
    frida_server_version: str
    pc_frida_server_xz_file_path: str
    pc_frida_server_file_path: str
    mobile_frida_server_file_path: str
    mobile_frida_server_process_name: str


class Frida:
    pc_dir_path: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), os.path.splitext(os.path.basename(__file__))[0]
    )
    mobile_dir_path = "/data/local/tmp/"

    def __init__(
            self,
            frida_server_xz_url: str | None = None,
            device_id: str | None = None,
            need_load_frida_data: bool = True,
    ):
        self.logger: Logger | None = None

        self.frida_server_xz_url: str = "https://github.com/frida/frida/releases/download/16.0.0/frida-server-16.0.0-android-arm.xz"
        if frida_server_xz_url:
            self.frida_server_xz_url = frida_server_xz_url

        self.device_id: str | None = None
        if device_id:
            self.device_id = device_id

        self.frida_data = self.parse_frida_server_xz_url(self.frida_server_xz_url)

        if need_load_frida_data:
            self.load_frida_data()
            self.push_frida_server()

        self.import_frida()

        self.device: _frida.Device | None = None
        self.session: _frida.Session | None = None
        self.script: _frida.Script | None = None

    def open_log(self) -> None:
        self.logger = get_logger()

    def close_log(self) -> None:
        self.logger = None

    if TYPE_CHECKING:
        @staticmethod
        def get_pc_local_host() -> str:
            ...
    else:
        get_pc_local_host = staticmethod(partial(get_host, host_type="local"))

    @classmethod
    def parse_frida_server_xz_url(cls, frida_server_xz_url: str) -> FridaData:
        segments = get_furl_obj(frida_server_xz_url).path.segments
        assert len(segments) == 6
        assert segments[0] == "frida"
        assert segments[1] == "frida"
        assert segments[2] == "releases"
        assert segments[3] == "download"
        frida_server_version = segments[4]

        frida_server_xz_file_name = os.path.basename(frida_server_xz_url)
        frida_server_file_name = re.sub(r"\.xz$", "", frida_server_xz_file_name, re.DOTALL)

        pc_frida_server_xz_file_path = os.path.join(cls.pc_dir_path, frida_server_xz_file_name)
        pc_frida_server_file_path = os.path.join(cls.pc_dir_path, frida_server_file_name)

        mobile_frida_server_file_path = (
            cls.mobile_dir_path + frida_server_file_name
            if cls.mobile_dir_path.endswith("/") else
            cls.mobile_dir_path + "/" + frida_server_file_name
        )
        mobile_frida_server_process_name = frida_server_file_name

        return FridaData(
            frida_server_xz_url,
            frida_server_version,
            pc_frida_server_xz_file_path,
            pc_frida_server_file_path,
            mobile_frida_server_file_path,
            mobile_frida_server_process_name
        )

    @classmethod
    def download_frida_server_xz(cls, frida_server_xz_url: str, pc_frida_server_xz_file_path: str) -> bool:
        if not frida_server_xz_url or not pc_frida_server_xz_file_path:
            return False

        if os.path.exists(pc_frida_server_xz_file_path):
            return True

        file_path = url_to_file_path(frida_server_xz_url, file_path=pc_frida_server_xz_file_path)
        return file_path == pc_frida_server_xz_file_path

    @classmethod
    def decompress_frida_server_xz(cls, pc_frida_server_xz_file_path: str, pc_frida_server_file_path: str) -> bool:
        if not pc_frida_server_xz_file_path or not pc_frida_server_file_path:
            return False

        if os.path.exists(pc_frida_server_file_path):
            return True

        with lzma.open(pc_frida_server_xz_file_path, "rb") as f_in, open(pc_frida_server_file_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)  # type: ignore
            return True

    def load_frida_data(self, frida_data: FridaData | None = None) -> None:
        if frida_data is None:
            frida_data = self.frida_data

        frida_server_xz_url = frida_data.frida_server_xz_url
        pc_frida_server_xz_file_path = frida_data.pc_frida_server_xz_file_path
        pc_frida_server_file_path = frida_data.pc_frida_server_file_path

        self.download_frida_server_xz(frida_server_xz_url, pc_frida_server_xz_file_path)
        self.decompress_frida_server_xz(pc_frida_server_xz_file_path, pc_frida_server_file_path)

    def execute_cmd_code_by_subprocess_popen(self, cmd_code: str, encoding: str | None = None) -> SubprocessPopenResult:
        if self.logger is None:
            return execute_cmd_code_by_subprocess_popen(cmd_code, encoding=encoding)
        return execute_cmd_code_by_subprocess_popen(cmd_code, encoding=encoding, logger=self.logger)

    def execute_cmd_code_by_subprocess_run(self, cmd_code: str, encoding: str | None = None) -> SubprocessRunResult:
        if self.logger is None:
            return execute_cmd_code_by_subprocess_run(cmd_code, encoding=encoding)
        return execute_cmd_code_by_subprocess_run(cmd_code, encoding=encoding, logger=self.logger)

    def pip_install_frida(self, frida_server_version: str | None = None) -> None:
        if not frida_server_version:
            frida_server_version = self.frida_data.frida_server_version

        text = self.execute_cmd_code_by_subprocess_popen('''pip show frida''').text
        if text == "WARNING: Package(s) not found: frida":
            self.execute_cmd_code_by_subprocess_popen(f"pip install frida=={frida_server_version}")
        else:
            if f"Version: {frida_server_version}" not in text:
                self.execute_cmd_code_by_subprocess_popen(
                    f"pip install --upgrade --force-reinstall frida=={frida_server_version}")

    def import_frida(self, frida_server_version: str | None = None) -> None:
        if frida_server_version is None:
            frida_server_version = self.frida_data.frida_server_version

        module_name = "frida"
        self.pip_install_frida(frida_server_version)
        module = importlib.import_module(module_name)
        globals()[module_name] = module

        module_name = "_frida"
        self.pip_install_frida(frida_server_version)
        module = importlib.import_module(module_name)
        globals()[module_name] = module

    def pip_install_frida_tools(self) -> None:
        text = self.execute_cmd_code_by_subprocess_popen("pip show frida-tools").text
        if text == "WARNING: Package(s) not found: frida-tools":
            self.execute_cmd_code_by_subprocess_popen("pip install frida-tools")

    def pip_install_frida_and_frida_tools(self, frida_server_version: str | None = None) -> None:
        if not frida_server_version:
            frida_server_version = self.frida_data.frida_server_version

        self.pip_install_frida(frida_server_version)
        self.pip_install_frida_tools()

    def push_frida_server(
            self,
            pc_frida_server_file_path: str | None = None,
            mobile_frida_server_file_path: str | None = None
    ) -> None:
        if not pc_frida_server_file_path:
            pc_frida_server_file_path = self.frida_data.pc_frida_server_file_path
        if not mobile_frida_server_file_path:
            mobile_frida_server_file_path = self.frida_data.mobile_frida_server_file_path

        text = self.execute_cmd_code_by_subprocess_run(
            f"adb shell test -e {mobile_frida_server_file_path} && echo 1 || echo 0"
        ).text
        if text == "0":
            self.execute_cmd_code_by_subprocess_run(
                f"adb push {pc_frida_server_file_path} {mobile_frida_server_file_path}"
            )

        text = self.execute_cmd_code_by_subprocess_run(
            f'''adb shell test -x {mobile_frida_server_file_path} && echo 1 || echo 0'''
        ).text
        if text == "0":
            self.execute_cmd_code_by_subprocess_run(f"adb shell chmod 755 {mobile_frida_server_file_path}")

    def check_frida_server_is_running(self, mobile_frida_server_process_name: str | None = None) -> bool:
        if not mobile_frida_server_process_name:
            mobile_frida_server_process_name = self.frida_data.mobile_frida_server_process_name

        return bool(self.execute_cmd_code_by_subprocess_run(f"adb shell pidof {mobile_frida_server_process_name}").text)

    def start_frida_server(
            self,
            mobile_frida_server_file_path: str | None = None,
            mobile_frida_server_process_name: str | None = None,
    ) -> None:
        if not mobile_frida_server_file_path:
            mobile_frida_server_file_path = self.frida_data.mobile_frida_server_file_path
        if not mobile_frida_server_process_name:
            mobile_frida_server_process_name = self.frida_data.mobile_frida_server_process_name

        if not self.check_frida_server_is_running(mobile_frida_server_process_name):
            self.execute_cmd_code_by_subprocess_run(
                f'''adb shell su -c "nohup {mobile_frida_server_file_path} >/dev/null 2>&1 &"'''
            )

    def init_device(self, mobile_frida_server_process_name: str | None = None) -> None:
        if not mobile_frida_server_process_name:
            mobile_frida_server_process_name = self.frida_data.mobile_frida_server_process_name

        if self.check_frida_server_is_running(mobile_frida_server_process_name):
            if self.device_id:
                self.device = frida.get_device(self.device_id)
            else:
                self.device = frida.get_usb_device(timeout=5)

    def stop_frida_server(self, mobile_frida_server_process_name: str | None = None) -> None:
        if not mobile_frida_server_process_name:
            mobile_frida_server_process_name = self.frida_data.mobile_frida_server_process_name

        if self.check_frida_server_is_running(mobile_frida_server_process_name):
            self.execute_cmd_code_by_subprocess_run(
                f'''adb shell su -c "kill -9 $(pidof {mobile_frida_server_process_name})"'''
            )

    def get_frontmost_application(self) -> _frida.Application | None:
        return self.device.get_frontmost_application()

    def get_processes(self) -> list[_frida.Process]:
        return self.device.enumerate_processes()

    def detach_session(self) -> None:
        if self.session is not None:
            self.session.detach()
            self.session = None
            if self.logger is not None:
                self.logger.debug("session detached")

    def spawn(self, package_names: list[str] | str) -> None:
        self.detach_session()

        if isinstance(package_names, str):
            package_names = [package_names]

        if not package_names:
            return

        pid = self.device.spawn(package_names)  # noqa
        self.session = self.device.attach(pid)
        self.device.resume(pid)
        if self.logger is not None:
            self.logger.debug(f"spawned package_names, package_names: {package_names}")

        seconds = random.uniform(1, 3)
        if self.logger is not None:
            self.logger.debug(f"random sleep for {seconds:.2f} seconds")

        time.sleep(seconds)

    def attach(self, pid_or_process_name: int | str) -> None:
        self.detach_session()

        if not pid_or_process_name:
            return

        self.session = self.device.attach(pid_or_process_name)
        if self.logger is not None:
            self.logger.debug(f"attached pid_or_process_name, pid_or_process_name: {pid_or_process_name}")

    def unload_script(self) -> None:
        if self.script is not None:
            self.script.unload()
            self.script = None
            if self.logger is not None:
                self.logger.debug("script unloaded")

    def load_script(self, js_file_path_or_js_code: str, on_message=None) -> None:
        self.unload_script()

        if not js_file_path_or_js_code:
            return

        if os.path.isfile(js_file_path_or_js_code) and os.path.exists(js_file_path_or_js_code):
            with open(js_file_path_or_js_code, "r", encoding="utf-8") as file:
                js_code = file.read()
        else:
            js_code = js_file_path_or_js_code

        self.script = self.session.create_script(js_code)

        def default_message(message, data):
            if message["type"] == "send":
                self.logger.success(f"[*] {message['payload']}")
            else:
                self.logger.debug(f"[*] {pprint.pformat(message)}")

        self.script.on("message", on_message or default_message)
        self.script.load()
        if self.logger is not None:
            self.logger.debug(f"script loaded, js_file_path_or_js_code: {js_file_path_or_js_code}")

    def close(self) -> None:
        self.unload_script()
        self.detach_session()

    def listen(self) -> None:
        try:
            for line in sys.stdin:
                if line.strip().lower() in ("exit", "quit"):
                    break
        except KeyboardInterrupt:
            if self.logger is not None:
                self.logger.warning(f"interrupted by user, cleaning up")
        finally:
            self.close()


if __name__ == '__main__':
    f = Frida()

    f.open_log()

    print(f.get_pc_local_host())

    f.start_frida_server()

    f.init_device()

    f.spawn("com.example.studyapplication")

    application = f.get_frontmost_application()
    print(application.pid, application.name)

    pid = application.pid
    f.attach(pid)

    for process in f.get_processes():
        print(process.pid, process.name)

    # language=JavaScript
    js_code = """
              Java.perform(function () {
                const NetworkDemoActivity = Java.use("com.example.studyapplication.NetworkDemoActivity");

                NetworkDemoActivity.okhttpGetSync.implementation = function () {
                  console.log(`arguments: ${JSON.stringify(arguments)}`);
                  const result = this.okhttpGetSync(...arguments);
                  console.log(`result: ${JSON.stringify(result)}`);
                  send("com.example.studyapplication.NetworkDemoActivity.okhttpGetSync called");
                  return result;
                };

              });
              """
    f.load_script(js_code)

    f.listen()

    f.stop_frida_server()

    f.close_log()
