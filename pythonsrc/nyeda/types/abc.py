
from abc import ABC, ABCMeta

class FeatureMeta(ABCMeta):
    def __new__(mcs, name, bases, namespace, /, **kwargs):
        if any(base.__name__ == 'Feature' for base in bases):
            if '__init__' in namespace:
                raise TypeError(
                    f"Class {name} cannot implement __init__ as it"
                    "is defined as a 'Feature'."
                )
        return super().__new__(mcs, name, bases, namespace, **kwargs)

class Feature(ABC, metaclass=FeatureMeta):
    pass
