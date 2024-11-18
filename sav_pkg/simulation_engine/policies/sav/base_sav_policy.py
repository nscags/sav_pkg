
from abc import ABC, abstractmethod

class BaseSAVPolicy(ABC):

    @staticmethod
    @abstractmethod
    def validate(self, *args, **kwargs) -> bool:
        """
        Performs validation policy on packet
        """
        pass