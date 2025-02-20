
from nyeda.types.archive import ArchByte, ArchByteInt
from nyeda.types.abc import Feature
from typing import Any

class preproc(Feature):
    """[`preproc`] Feature.
    
    This feature enables a preprocessing feature for internal
    archive data type conversion and checking.
    """
    def preproc(self, content: Any) -> ArchByte[ArchByteInt]:
        """Makes the data processable if necessary before moving
        on to further processing."""