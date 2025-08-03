from typing import Any


def list_dict_to_str(cookies_list_dict: list[dict[str, Any]]) -> str:
    return "; ".join([c["name"] + "=" + c["value"] for c in cookies_list_dict])


def str_to_dict(cookies_str: str) -> dict[str, str]:
    return {c.split("=")[0].strip(): c.split("=")[-1].strip() for c in cookies_str.split(";")}


def dict_to_str(cookies_dict: dict[str, str]) -> str:
    return "; ".join([k + "=" + v for k, v in cookies_dict.items()])
