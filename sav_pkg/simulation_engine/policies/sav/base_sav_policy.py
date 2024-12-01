from abc import ABC, abstractmethod


class BaseSAVPolicy(ABC):
    name: str = "NoSAV"

    @staticmethod
    @abstractmethod
    def validate(self, *args, **kwargs) -> bool:
        """
        Performs validation policy on packet
        """
        pass
