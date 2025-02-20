
from nyeda.bin.sharedobject import bundle
from nyeda.types.archive import ArchByte, ArchByteInt
from nyeda.exceptions import NYEDASEG, NYEDAException
from nyeda.types.abc import Feature
from pathlib import Path

class bundler(Feature):
    def bundle(self, source: Path) -> ArchByte[ArchByteInt]:
        # make source completely absolute to support relate
        # paths as parameters
        source = source.expanduser().resolve()

        # make sure the source exists and is a directory.
        if not source.exists():
            return NYEDASEG(NYEDAException, 'source path does not exist! (via. bundler)')
        if source.is_file():
            return NYEDASEG(NYEDAException, 'source path must be a directory! (via. bundler)')
        
        # create the bundle using bundle module.
        __bundle__ = bundle.Bundle().create(str(source), 1)

        # return the bundle in ArchBytes Format
        return ArchByte(__bundle__)