from abc import ABC, abstractmethod

class BaseSAVPolicy(ABC):
    @abstractmethod
    def validate(self, as_obj, prev_hop, engine, as_path):
        raise NotImplementedError