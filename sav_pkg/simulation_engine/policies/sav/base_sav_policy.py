from abc import ABC, abstractmethod

class BaseSAVPolicy(ABC):
    @abstractmethod
    def validate(self):
        raise NotImplementedError