# type: ignore

from typing import Type, Any, Dict, Tuple
from abc import ABC, ABCMeta

class FeatureMeta(ABCMeta):
    def __new__(
            mcs: Type['FeatureMeta'],
            name: str,
            bases: Tuple[Type[Any], ...],
            namespace: Dict[str, Any],
    ) -> Type['FeatureMeta']:
        """Explicitly checks if any class that is defined as a Feature
        must not contain an `__init__` method. However, any grandchild
        (Inheriter of the feature) can have it."""

class Feature(ABC, metaclass=FeatureMeta):
    """Feature maker for bulky code bases.
    
    Any class inheriting this class must not define a `__init__` method.
    Doing so will result in `TypeError`.

    Example usage:
    ```python
    # This is a feature for some larger agenda
    class Logging(Feature):
        def log(text: str) -> None: ...
    
    # Usage class
    class App(Logging):
        def __init__(self) -> None: ...
            # the logging feature can be used here
            # or at any point inside the App class.
            self.log('Initializing...')
    ```
    """