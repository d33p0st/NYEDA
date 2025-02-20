
from nyeda.types.archive import ArchByte, ArchByteInt
from nyeda.types.abc import Feature

class dismantler(Feature):
    """[`dismantler`] Feature.
    
    This feature provides the `dismantle` method to break archive data
    into system interpretable format.
    """
    def dismantle(self, content: ArchByte[ArchByteInt]) -> ArchByte[ArchByteInt]:
        """Dismantle archive data into system readable format."""