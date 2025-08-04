from dataclasses import dataclass


@dataclass(frozen=True)
class AccountDataclass(object):
    owner: str
    platform: str
    username: str
    password: str
