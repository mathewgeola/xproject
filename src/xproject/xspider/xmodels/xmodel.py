from abc import ABC, abstractmethod


class Model(ABC):
    @classmethod
    @abstractmethod
    def columns(cls) -> list[str]:
        pass
