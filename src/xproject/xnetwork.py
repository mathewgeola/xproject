import socket
from typing import Literal

import httpx


def check_port_occupancy(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        port_occupied = s.connect_ex(("127.0.0.1", port)) == 0
        return port_occupied


def get_host(host_type: Literal["local", "public"] = "local") -> str:
    if host_type == "local":
        return socket.gethostbyname(socket.gethostname())
    elif host_type == "public":
        return httpx.get("https://api.ipify.org", timeout=60).text
    else:
        raise ValueError(
            f"Invalid type for 'host_type': "
            f"Expected `Literal[\"local\", \"public\"]`, "
            f"but got {type(host_type).__name__!r} (value: {host_type!r})"
        )


if __name__ == '__main__':
    print(get_host())
    print(get_host("public"))
