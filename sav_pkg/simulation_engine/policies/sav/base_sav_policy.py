from abc import ABC, abstractmethod

class BaseSAVPolicy(ABC):
    @abstractmethod
    def validate(self, as_obj, prev_hop, origin, engine):
        raise NotImplementedError