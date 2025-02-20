
from nyeda.types.archive import ArchByte, ArchByteInt
from nyeda.types.abc import Feature
from pathlib import Path

class bundler(Feature):
    """[`bundler`] Feature.
    
    This feature provides a `bundle` method to safely bundle any source
    directory with current system metadata.
    
    Boasts a `Rust` backend for enhanced speed (as compared to python
    code).
    """
    def bundle(self, source: Path) -> ArchByte[ArchByteInt]:
        """Rapidly bundles a source directory into `ArchByte` format using
        a `Rust` backend."""